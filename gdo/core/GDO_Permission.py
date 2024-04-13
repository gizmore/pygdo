from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_Permission(GDO):

    def __init__(self):
        super().__init__()

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('perm_id'),
            GDT_Name('perm_name'),
        ]

    def count(self):
        return GDO_UserPermission.where('permu')
