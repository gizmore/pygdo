from gdo.core.GDO_Module import GDO_Module
from gdo.core.GDO_ModuleVar import GDO_ModuleVar


class module_core(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 1

    def gdo_init(self):
        pass

    def gdo_dependencies(self) -> list:
        return [
            'language',
            'user',
        ]

    def gdo_classes(self):
        return [
            GDO_Module,
            GDO_ModuleVar,
        ]

