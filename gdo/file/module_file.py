from gdo.base.GDO_Module import GDO_Module
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.base.GDO import GDO
from gdo.ui.GDT_Link import GDT_Link

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page

class module_file(GDO_Module):
    
    def __init__(self):
        super().__init__()
        self._priority = 19

    def gdo_classes(self) -> list[type[GDO]]:
        from gdo.core.GDO_File import GDO_File
        return [
            GDO_File,
            GDO_SeoFile,
        ]

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_bower_js('flow.js/lib/flow.js')
        self.add_js('js/gdo-flow.js')
        self.add_css('css/pygdo-file.css')

    def gdo_admin_links(self) -> list['GDT_Link']:
        return [
            GDT_Link().href(self.href('files')).text('mt_files_files'),
            GDT_Link().href(self.href('seofiles')).text('mt_files_seofiles'),
        ]
