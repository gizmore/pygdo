from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.language.GDO_Language import GDO_Language
from gdo.language.GDT_Language import GDT_Language


class module_language(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_classes(self):
        return [
            GDO_Language,
        ]

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Language('language').initial('en'),
        ]