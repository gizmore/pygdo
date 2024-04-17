from mod_python import Cookie

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_User import GDT_User
from gdo.net.GDT_IP import GDT_IP


class GDO_Session(GDO):
    _req: object
    _cookies: dict[str, str]
    _data: dict[str, any]

    def __init__(self):
        super().__init__()
        self._req = None
        self._cookies = {}
        self._data = {}

    @classmethod
    def start(cls, req):
        instance = cls().request(req).cookies(Cookie.get_cookies(req))
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
        return self.gdo_value('sess_user')

    def request(self, req):
        self._req = req
        return self

    def cookies(self, cookies):
        self._cookies = cookies
        return self

    def set(self, key: str, value):
        self._data[key] = value
        return self

    def get(self, key: str):
        return self._data[key]

    def save(self):
        self.set_value('sess_data', self._data)
        return super().save()

