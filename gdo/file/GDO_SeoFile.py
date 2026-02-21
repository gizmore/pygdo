from functools import lru_cache

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.core.GDT_String import GDT_String

from typing import  TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_File import GDO_File


class GDO_SeoFile(GDO):

    def gdo_columns(self) -> list[GDT]:
        from gdo.file.GDT_File import GDT_File
        return [
            GDT_String('sf_url').maxlen(172).primary().unique().case_s().not_null(),
            GDT_File('sf_file').not_null(),
        ]

    def get_file(self) -> 'GDO_File':
        return self.gdo_value('sf_file')[0]

    @classmethod
    # @lru_cache(maxsize=1024)
    def get_by_url(cls, url: str) -> 'GDO_SeoFile':
        url = Strings.substr_to(url, '?', url).strip('/')
        return cls.table().get_by_aid(url)
