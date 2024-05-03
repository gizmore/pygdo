from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_Method(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('m_id'),
            GDT_Name('m_name'),
        ]
