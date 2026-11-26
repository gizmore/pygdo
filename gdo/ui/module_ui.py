from gdo.base.GDO_Module import GDO_Module
from gdo.ui.GDT_Font import GDT_Font
from gdo.ui.IconProvider import IconProvider
from gdo.ui.IconUTF8 import IconUTF8
from gdo.base.GDO import GDO


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page


class module_ui(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 8

    def gdo_classes(self) -> list[type[GDO]]:
        return []

    def gdo_init(self):
        IconProvider.register(IconUTF8)
        GDT_Font.register('Arial', self.file_path('font/Arial.ttf'))

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_js('js/pygdo-ui.js')
        self.add_css('css/pygdo-ui.css')
