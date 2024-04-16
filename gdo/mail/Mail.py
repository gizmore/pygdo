from gdo.core.GDO_User import GDO_User


class Mail:
    _sender: str
    _recipient: str
    _lazy: bool
    _subject: str
    _body: str
    _attachments: dict[str, str]

    @classmethod
    def from_bot(cls):
        return cls().sender()

    def __init__(self):
        self._lazy = False

    def sender(self, email: str, name: str = None):
        if name:
            self._sender = f"{name}<{email}>"
        else:
            self._sender = email
        return self

    def recipient(self, email: str, name: str = None):
        if name:
            self._sender = f"{name}<{email}>"
        else:
            self._sender = email
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