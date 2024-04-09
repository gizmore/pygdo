from gdo.core.GDO_Module import GDO_Module
from gdo.language.GDO_Language import GDO_Language


class module_language(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_classes(self):
        return [
            GDO_Language,
        ]