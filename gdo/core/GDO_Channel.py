from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created


class GDO_Channel(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('chan_id'),
            GDT_Name('chan_name'),
            GDT_String('chan_displayname'),
            GDT_Created('chan_created'),
            GDT_Creator('chan_creator'),
        ]
