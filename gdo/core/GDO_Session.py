from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Edited import GDT_Edited
from gdo.net.GDT_IP import GDT_IP


class GDO_Session(GDO):
    LIFETIME = 60 * 60 * 24 * 7
    COOKIE_NAME = 'GDO'
    DEFAULT_COOKIE = 'gdo_like_16_byte'

    _data: dict[str, any]

    __slots__ = (
        '_data',
    )

    def __init__(self):
        super().__init__()
        self._data = {}

    def __repr__(self):
        return f"{self.get_name()}()"

    @classmethod
    def start(cls, create_session: bool):
        """
        Start a HTTP session.
        :param create_session: If False, do not create a session, only load an existing one. If True, turn  16 byte cookie into real session and save.
        """
        cookie = Application.get_cookie(cls.COOKIE_NAME)
        if cookie == cls.DEFAULT_COOKIE:
            instance = cls.blank({
                'sess_token': GDT_Token.random(),
            })
            if create_session:  # Only create a session if wanted. We do not want to create sessions on file_server()
                instance.save()
                instance.set_header()
        elif cookie:
            instance = cls.for_cookie(cookie)
        else:
            instance = cls.blank_error()
        Application.set_session(instance)
        return instance

    @classmethod
    def set_default_header(cls):
        cls.set_cookie_header(cls.DEFAULT_COOKIE)

    @classmethod
    def set_cookie_header(cls, cookie: str):
        http_only = ' HttpOnly;'
        # secure = ' Secure;'
        secure = ''
        same_site = f' SameSite={Application.config('sess.same_site', 'lax')};'
        Application.header('Set-Cookie', f"{cls.COOKIE_NAME}={cookie}; Path=/;{http_only}{secure}{same_site}")

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
        instance = cls.table().get_by_aid(id_)
        if not instance:
            return cls.blank_error()
        if instance.get_token() != token:
            return cls.blank_error()
        ip = instance.get_ip()
        if ip and ip != GDT_IP.current():
            return cls.blank_error()
        instance._data = instance.gdo_value('sess_data') or None
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
        else:
            session._data = session.gdo_value('sess_data') or {}
        user._session = session
        return session

    def gdo_table_engine(self) -> str:
        return 'InnoDB'

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('sess_id'),
            GDT_Token('sess_token'),
            GDT_User('sess_user'),
            GDT_IP('sess_ip'),
            GDT_Serialize('sess_data'),
            GDT_Edited('sess_time'),
        ]

    def save(self):
        if self._data:
            self.set_value('sess_data', self._data)
        if self.get_token() == self.DEFAULT_COOKIE:
            return self
        return super().save()

    def set_header(self):
        self.set_cookie_header(self.cookie_value())

    def cookie_value(self) -> str:
        return f"{self.get_id()}:{self.get_token()}"

    def get(self, key: str, default: any = None):
        return self._data.get(key, default) if self._data else default

    def set(self, key: str, value):
        self._data = {} if self._data is None else self._data
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
        return uid or '0'

    def get_ip(self) -> str | None:
        return self.gdo_val('sess_ip')

    def get_user(self) -> GDO_User:
        if user := self.gdo_value('sess_user'):
            user._authenticated = True
            user._session = self
        return user or GDO_User.ghost()
