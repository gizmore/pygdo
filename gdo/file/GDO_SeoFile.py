from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_File import GDO_File

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_String import GDT_String


class GDO_SeoFile(GDO):

    FILES = {}

    def gdo_columns(self) -> list[GDT]:
        from gdo.file.GDT_File import GDT_File
        return [
            GDT_AutoInc('sf_id'),
            GDT_String('sf_url').unique().case_s().not_null(),
            GDT_File('sf_file').not_null(),
        ]

    @classmethod
    def get_by_url(cls, url: str) -> 'GDO_File':
        url = url.lstrip('/')
        url = Strings.substr_to(url, '?', url).rstrip('/')
        if url in cls.FILES:
            return cls.FILES.get(url)
        cls.FILES[url] = file = cls.table().get_by('sf_url', url)
        return file
