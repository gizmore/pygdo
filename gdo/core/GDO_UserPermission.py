from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Permission import GDT_Permission
from gdo.core.GDT_User import GDT_User


class GDO_UserPermission(GDO):

    def __init__(self):
        super().__init__()

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_User('pu_user').primary(),
            GDT_Permission('pu_perm').primary(),
        ]