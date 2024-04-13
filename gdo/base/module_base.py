from packaging.version import Version

from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO_ModuleVar import GDO_ModuleVar


class module_base(GDO_Module):

    CORE_VERSION = Version("8.0.0")

    def __init__(self):
        super().__init__()
        self._priority = 0

    def gdo_classes(self):
        return [
            GDO_Module,
            GDO_ModuleVar,
        ]
