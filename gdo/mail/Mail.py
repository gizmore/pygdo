from gdo.base.Application import Application
from gdo.core.GDO_User import GDO_User


class Mail:
    _sender: str
    _recipients: list[str]
    _cc: list[str]
    _bcc: list[str]
    _lazy: bool
    _subject: str
    _body: str
    _attachments: dict[str, str]

    def _cfg(self) -> dict[str, str]:
        return Application.CONFIG['mail']

    @classmethod
    def from_bot(cls):
        return cls().sender()

    def __init__(self):
        self._lazy = False
        self._recipients = []

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
        self.recipient(user.get_mail(), user.get_val('user_displayname'))
        return self.send()

    def send(self) -> bool:
        pass
