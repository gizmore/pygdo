from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Secret import GDT_Secret
from gdo.date.GDT_Created import GDT_Created
from gdo.net.GDT_Url import GDT_Url


class GDO_Server(GDO):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_by_connector(cls, name: str):
        return cls.table().select().where(f"serv_connector={GDT.quote(name)}").first().exec().fetch_object()

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

    def get_or_create_user(self, username: str):
        user = self.get_user_by_name(username)
        if not user:
            user = self.create_user(username)
        return user

    def get_user_by_name(self, username):
        pass

    def create_user(self, username):
        pass


