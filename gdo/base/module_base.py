from packaging.version import Version

from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO_ModuleVar import GDO_ModuleVar
from gdo.base.GDT import GDT
from gdo.core.GDT_Bool import GDT_Bool


class module_base(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 0

    def gdo_classes(self):
        return [
            GDO_Module,
            GDO_ModuleVar,
        ]

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('500_mails').initial('1'),
        ]
