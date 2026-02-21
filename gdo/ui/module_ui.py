from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
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

    def gdo_module_config(self) -> list[GDT]:
        from gdo.core.GDT_Bool import GDT_Bool
        return [
            GDT_Bool('scroll_to_top').initial('1').not_null(),
        ]

    def gdo_classes(self) -> list[type[GDO]]:
        return []

    def gdo_init(self):
        IconProvider.register(IconUTF8)
        GDT_Font.register('Arial', self.file_path('font/Arial.ttf'))

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_js('js/pygdo-ui.js')

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        if self.get_config_value('scroll_to_top'):
            from gdo.ui.GDT_Button import GDT_Button
            page._bottom_bar.add_field(GDT_Button('stt').attr('onclick', 'gdo.ui.scrollToTop()').text('scroll_up').icon('arrow_up'))
