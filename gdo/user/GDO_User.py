from gdo.core.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_User(GDO):

    def gdo_columns(self) -> list:
        return [
            GDT_AutoInc('user_id'),
            GDT_Name('user_name').unique()
        ]
