import pickle
import smtplib
import imaplib
from pathlib import Path
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Util import Strings
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Template import tpl
from gdo.mail.GDO_Mail import GDO_Mail
from gdo.message.GDT_HTML import GDT_HTML


class Mail:
    SENT = 0
    _sender: str
    _reply: str
    _recipients: list[str]
    _cc: list[str]
    _bcc: list[str]
    _lazy: bool
    _subject: str
    _body: str
    _attachments: list[tuple[Path, str]]

    @classmethod
    def _cfg(cls, key: str) -> str:
        return Application.config(f'mail.{key}')

    @classmethod
    def from_bot(cls):
        mail = cls().sender(cls._cfg('sender'), cls._cfg('sender_name'))
        if reply_to := cls._cfg('reply_to'):
            mail.reply_to(reply_to)
        return mail

    @classmethod
    def is_debug(cls):
        return Application.config('mail.debug', '1') != '0'

    def __init__(self):
        self._lazy = False
        self._recipients = []
        self._cc = []
        self._bcc = []
        self._reply = ''
        self._attachments = []

    def lazy(self, lazy: bool = True):
        self._lazy = lazy
        return self

    def _ma(self, email: str, name: str = None) -> str:
        if name:
            return f"{name}<{email}>"
        else:
            return email

    def sender(self, email: str, name: str = None):
        self._sender = self._ma(email, name)
        return self

    def recipient(self, email: str, name: str = None):
        self._recipients.append(self._ma(email, name))
        return self

    def reply_to(self, email: str, name: str = None):
        self._reply = self._ma(email, name)
        return self


    def cc(self, email: str, name: str = None):
        self._cc.append(self._ma(email, name))
        return self

    def bcc(self, email: str, name: str = None):
        self._bcc.append(self._ma(email, name))
        return self

    def subject(self, subject: str):
        self._subject = subject
        return self

    def body(self, body: str):
        self._body = body
        return self

    def attachment(self, path: str | Path, name: str = None):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        self._attachments.append((path, name or path.name))
        return self

    def send_to_user(self, user: GDO_User) -> bool:
        self.recipient(user.get_mail(), user.get_displayname())
        return self.send()

    def send(self) -> bool:
        self.SENT += 1
        if self.is_debug():
            self.print_mail_to_screen()
            self.log_mail()
            return True
        if self._lazy:
            GDO_Mail.blank({
                'mail_receiver': ", ".join(self._recipients),
                'mail_subject': self._subject,
                'mail_mail': pickle.dumps(self),
            }).insert()
            return True
        return self.really_send_mail()

    def print_mail_to_screen(self):
        Application.get_page()._top_bar.add_field(GDT_HTML().text(self._body_text()))

    def log_mail(self):
        Logger.write('mail.log', self._subject, False)
        Logger.write('mail.log', '-'*48, False)
        Logger.write('mail.log', self._body_text(), False)
        Logger.write('mail.log', '-'*48, False)
        Logger.write('mail.log', self._body_html(), False)
        Logger.write('mail.log', '-'*48, False)

    def _body_html(self) -> str:
        return tpl('mail', 'mail.html', {"mail": self})

    def _body_text(self) -> str:
        return Strings.html_to_text(self._body)

    def build_message(self):
        message = MIMEMultipart()
        message["From"] = self._sender
        message["To"] = ",".join(self._recipients)
        if self._reply:
            message["Reply-To"] = self._reply
        if self._cc:
            message["Cc"] = ",".join(self._cc)
        message["Subject"] = self._subject
        message.attach(MIMEText(self._body_html(), "html"))
        message.attach(MIMEText(self._body_text(), "plain"))
        for path, name in self._attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(path.read_bytes())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=name)
            message.attach(part)
        return message

    def really_send_mail(self):
        port = int(Application.config('mail.port'))
        smtp_server = Application.config('mail.host')
        login = Application.config('mail.user')
        password = Application.config('mail.pass')

        sender_email = self._sender
        receiver_email = list(dict.fromkeys([*self._recipients, *self._cc, *self._bcc]))
        message = self.build_message()

        # Send the email
        with smtplib.SMTP(smtp_server, port) as server:
            if Application.config('mail.tls', '1') == '1':
                server.starttls()
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        try:
            self.store_in_sent(message)
        except Exception as ex:
            # SMTP has already accepted the message. Do not turn an archive
            # failure into a retry that could deliver a duplicate email.
            Logger.exception(ex, 'Mail was sent but could not be stored in Sent.')

        return True

    def store_in_sent(self, message) -> None:
        """Append a successfully submitted message to the sender mailbox."""
        if Application.config('mail.store_sent', '0') != '1':
            return
        host = Application.config('mail.imap_host')
        port = int(Application.config('mail.imap_port', '993'))
        # A normal Dog mailbox uses the same submission credentials for IMAP.
        # Dedicated IMAP credentials remain possible without duplicating the
        # common password in the configuration by default.
        user = Application.config('mail.imap_user') or Application.config('mail.user')
        password = Application.config('mail.imap_pass') or Application.config('mail.pass')
        folder = Application.config('mail.imap_sent_folder', 'Sent')
        if not all((host, user, password, folder)):
            raise ValueError('Sent-mail storage is enabled but IMAP configuration is incomplete.')
        client_class = imaplib.IMAP4_SSL if Application.config('mail.imap_ssl', '1') == '1' else imaplib.IMAP4
        with client_class(host, port) as client:
            client.login(user, password)
            status, _data = client.append(client._quote(folder), '\\Seen', None, message.as_bytes())
            if status != 'OK':
                raise RuntimeError(f'Could not append sent mail to {folder}: {status}')
