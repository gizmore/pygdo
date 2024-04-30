from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Created import GDT_Created


class GDO_File(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('file_id'),
            GDT_Name('file_name').not_null(),
            GDT_UInt('file_size').not_null(),
            GDT_String('file_mime').not_null(),
            GDT_MD5('file_hash').not_null(),
            GDT_Created('file_created'),
            GDT_Creator('file_creator'),
        ]
