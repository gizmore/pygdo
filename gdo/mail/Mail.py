import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from gdo.base.Application import Application
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
    _attachments: dict[str, str]

    @classmethod
    def _cfg(cls, key: str) -> dict[str, str]:
        return Application.config(f'mail')

    @classmethod
    def from_bot(cls):
        return cls().sender(cls._cfg('sender'), cls._cfg('sender_name'))

    @classmethod
    def is_debug(cls):
        return Application.config('mail.debug', '1') != '0'

    def __init__(self):
        self._lazy = False
        self._recipients = []

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

    def send_to_user(self, user: GDO_User) -> bool:
        self.recipient(user.get_mail(), user.gdo_val('user_displayname'))
        return self.send()

    def send(self) -> bool:
        self.SENT += 1
        if self.is_debug():
            self.print_mail_to_screen()
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
        Application.get_page()._top_bar.add_field(GDT_HTML().val(self._body_text()))
        pass

    def _body_html(self) -> str:
        return tpl('mail', 'mail.html', {"mail": self})

    def _body_text(self) -> str:
        return Strings.html_to_text(self._body)

    def really_send_mail(self):
        # Configuration
        port = int(Application.config('mail.port'))
        smtp_server = Application.config('mail.host')
        login = Application.config('mail.user')
        password = Application.config('mail.pass')

        sender_email = self._sender
        receiver_email = self._recipients

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self._sender
        message["To"] = self._recipients
        message["Subject"] = self._subject

        message.attach(MIMEText(self._body_html(), "html"))

        # Add body to email
        message.attach(MIMEText(self._body_text(), "plain"))

        # # Specify the attachment file path
        # filename = "path/to/your/file.pdf"  # Change this to the correct path
        #
        # # Open the file in binary mode
        # with open(filename, "rb") as attachment:
        #     part = MIMEBase("application", "octet-stream")
        #     part.set_payload(attachment.read())
        #
        # # Encode file in ASCII characters to send by email
        # encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        # part.add_header("Content-Disposition", f"attachment; filename= {filename}")

        # Add attachment to message
        # message.attach(part)

        # Send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return True
