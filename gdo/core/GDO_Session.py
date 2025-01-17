from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_User import GDT_User
from gdo.net.GDT_IP import GDT_IP


class GDO_Session(GDO):
    COOKIE_NAME = 'GDO'
    DEFAULT_COOKIE = 'gdo_like_16_byte'
    _data: dict[str, any]

    def __init__(self):
        super().__init__()
        self._data = {}

    @classmethod
    def start(cls, create_session: bool):
        """
        Start a HTTP session.
        :param create_session: If False, do not create a session, only load an existing one. If True, turn  16 byte cookie into real session and save.
        """
        cookie = Application.get_cookie(cls.COOKIE_NAME)
        if cookie == cls.DEFAULT_COOKIE:
            token = GDT_Token.random()
            instance = cls.blank({
                'sess_token': token,
            })
            if create_session:  # Only create a session if wanted. We do not want to create sessions on file_server()
                instance.save()
                instance.set_header()
        elif cookie:
            instance = cls.for_cookie(cookie)
        else:
            instance = cls.blank_error()
        return instance

    @classmethod
    def set_default_header(cls):
        cls.set_cookie_header(cls.DEFAULT_COOKIE)

    @classmethod
    def set_cookie_header(cls, cookie: str):
        Application.header('Set-Cookie', f"{cls.COOKIE_NAME}={cookie}; Path=/")

    @classmethod
    def blank_error(cls):
        instance = cls.blank({
            'sess_token': cls.DEFAULT_COOKIE,
        })
        cls.set_default_header()
        return instance

    @classmethod
    def for_cookie(cls, cookie: str):
        parts = cookie.split(':')
        if len(parts) != 2:
            return cls.blank_error()
        id_, token = parts
        instance = cls.table().get_by_id(id_)
        if not instance:
            return cls.blank_error()
        if instance.get_token() != token:
            return cls.blank_error()
        ip = instance.get_ip()
        if ip and ip != GDT_IP.current():
            return cls.blank_error()
        return instance

    @classmethod
    def for_user(cls, user: GDO_User | object):
        """
        Call this for non HTTP sessions.
        """
        session = cls.table().get_by_vals({
            'sess_user': user.get_id(),
        })
        if not session:
            session = cls.blank({
                'sess_token': GDT_Token.random(),
                'sess_user': user.get_id(),
            }).insert()
        return session

    def gdo_engine_fast(self) -> bool:
        return True

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('sess_id'),
            GDT_Token('sess_token'),
            GDT_User('sess_user'),
            GDT_IP('sess_ip'),
            GDT_Serialize('sess_data'),
        ]

    def save(self):
        if self.get_token() == self.DEFAULT_COOKIE:
            return self
        self.set_value('sess_data', self._data)
        return super().save()

    def set_header(self):
        self.set_cookie_header(self.cookie_value())

    def cookie_value(self) -> str:
        return f"{self.get_id()}:{self.get_token()}"

    def get(self, key: str, default: any = None):
        return self._data[key] if key in self._data else default

    def set(self, key: str, value):
        self._data[key] = value
        return self

    def remove(self, key: str):
        if key in self._data:
            del self._data[key]
        return self

    def get_token(self) -> str:
        return self.gdo_val('sess_token')

    def get_uid(self) -> str:
        uid = self.gdo_val('sess_user')
        return '0' if not uid else uid

    def get_ip(self) -> str | None:
        return self.gdo_val('sess_ip')

    def get_user(self) -> GDO_User:
        if user := self.gdo_value('sess_user'):
            user._authenticated = True
        return user or GDO_User.ghost()
