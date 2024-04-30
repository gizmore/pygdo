from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.core.Connector import Connector
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Secret import GDT_Secret
from gdo.date.GDT_Created import GDT_Created
from gdo.net.GDT_Url import GDT_Url


class GDO_Server(GDO):
    _connector: Connector

    def __init__(self):
        super().__init__()

    @classmethod
    def get_by_connector(cls, name: str):
        return cls.table().get_by_vals({"serv_connector": name})

    def gdo_columns(self) -> list[GDT]:
        from gdo.core.GDT_Creator import GDT_Creator
        return [
            GDT_AutoInc('serv_id'),
            GDT_Name('serv_name'),
            GDT_Url('serv_url'),
            GDT_Name('serv_username'),
            GDT_Secret('serv_password'),
            GDT_Connector('serv_connector'),
            GDT_Created('serv_created'),
            GDT_Creator('serv_creator'),
        ]

    def get_url(self) -> dict:
        return self.gdo_value('serv_url')

    def get_host(self):
        return self.get_url()['host']

    def get_connector(self):
        if not hasattr(self, '_connector'):
            self._connector = self.gdo_value('serv_connector')
            self._connector.server(self)
        return self._connector

    def get_or_create_user(self, username: str, displayname: str = None):
        user = self.get_user_by_name(username)
        if not user:
            user = self.create_user(username, displayname or username)
        return user

    def get_user_by_name(self, username):
        return GDO_User.table().get_by_vals({
            'user_server': self.get_id(),
            'user_name': username,
        })

    def get_users_with_setting(self, key: str, val: str, op: str = '=') -> Query:
        return GDO_UserSetting.get_users_with_setting(self.get_id(), key, val, op)

    def create_user(self, username: str, displayname: str = None):
        return GDO_User.blank({
            'user_name': username,
            'user_displayname': username or displayname,
            'user_server': self.get_id(),
        }).insert()

    def is_connected(self):
        return self.get_connector().is_connected()

    def is_connecting(self):
        return self.get_connector().is_connecting()
