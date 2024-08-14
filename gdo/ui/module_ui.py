from gdo.base.GDO_Module import GDO_Module
from gdo.ui.GDT_Font import GDT_Font
from gdo.ui.IconProvider import IconProvider
from gdo.ui.IconUTF8 import IconUTF8


class module_ui(GDO_Module):

    def gdo_classes(self):
        return []

    def gdo_init(self):
        IconProvider.register(IconUTF8)
        GDT_Font.register('Arial', self.file_path('font/Arial.ttf'))
