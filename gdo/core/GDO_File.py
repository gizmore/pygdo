from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Duration import GDT_Duration
from gdo.ui.GDT_Height import GDT_Height
from gdo.ui.GDT_Width import GDT_Width


class GDO_File(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('file_id'),
            GDT_Name('file_name').not_null(),
            GDT_UInt('file_size').not_null(),
            GDT_String('file_mime').not_null(),
            GDT_MD5('file_hash').not_null(),
            GDT_Duration('file_duration'),
            GDT_Width('file_width'),
            GDT_Height('file_height'),
            GDT_Created('file_created'),
            GDT_Creator('file_creator'),
        ]

    def get_mime(self) -> str:
        return self.gdo_val('file_mime')

    def is_image(self) -> bool:
        return self.get_mime() in GDT_MimeType.IMAGE_TYPES
