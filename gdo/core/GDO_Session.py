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
    def start(cls):
        cookie = Application.get_cookie(cls.COOKIE_NAME)
        if cookie == cls.DEFAULT_COOKIE:
            token = GDT_Token.random()
            instance = cls.blank({
                'sess_token': token,
            })
            instance.save()
            instance.set_header()
            return instance
        elif cookie:
            return cls.for_cookie(cookie)
        else:
            return cls.blank_error()

    @classmethod
    def set_default_header(cls):
        cls.set_cookie_header(cls.DEFAULT_COOKIE)

    @classmethod
    def set_cookie_header(cls, cookie: str):
        Application.header('Set-Cookie', f"{cls.COOKIE_NAME}={cookie}; Path=/")

    def set_header(self):
        self.set_cookie_header(self.cookie_value())

    @classmethod
    def for_cookie(cls, cookie: str):
        parts = cookie.split(':')
        if len(parts) != 3:
            return cls.blank_error()
        id_, uid, token = parts
        instance = cls.table().get_by_id(id_)
        if not instance:
            return cls.blank_error()
        if instance.get_uid() != uid:
            return cls.blank_error()
        if instance.get_token() != token:
            return cls.blank_error()
        return instance

    @classmethod
    def for_user(cls, user: GDO_User):
        session = cls.table().get_by_vals({
            'sess_user': user.get_id(),
        })
        if not session:
            session = cls.blank({
                'sess_token': GDT_Token.random(),
                'sess_user': user.get_id(),
            }).insert()
        return session

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('sess_id'),
            GDT_Token('sess_token'),
            GDT_User('sess_user'),
            GDT_IP('sess_ip'),
            GDT_Serialize('sess_data'),
        ]

    def get_user(self) -> GDO_User:
        user = self.gdo_value('sess_user')
        return GDO_User.ghost() if not user else user

    def set(self, key: str, value):
        self._data[key] = value
        return self

    def get(self, key: str, default: str = None):
        return self._data[key] if key in self._data else default

    def save(self):
        self.set_value('sess_data', self._data)
        return super().save()

    def get_token(self) -> str:
        return self.gdo_val('sess_token')

    def cookie_value(self) -> str:
        return f"{self.get_id()}:{self.get_uid()}:{self.get_token()}"

    def get_uid(self) -> str:
        uid = self.gdo_val('sess_user')
        return '0' if not uid else uid

    @classmethod
    def blank_error(cls):
        instance = cls.blank({
            'sess_token': cls.DEFAULT_COOKIE,
        })
        cls.set_default_header()
        return instance
