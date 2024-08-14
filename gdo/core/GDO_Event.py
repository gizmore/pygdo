from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created


class GDO_Event(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('event_id'),
            GDT_String('event_name').primary().not_null(),
            GDT_Serialize('event_args'),
            GDT_Created('event_created'),
        ]
