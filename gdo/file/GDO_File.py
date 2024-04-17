from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Created import GDT_Created


class GDO_File(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('file_id'),
            GDT_String('file_name'),
            GDT_UInt('file_size'),
            GDT_String('file_mime'),
            GDT_Created('file_created'),
        ]
