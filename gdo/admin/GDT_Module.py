from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDT_Object import GDT_Object


class GDT_Module(GDT_Object):
    _enabled: bool | None

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_Module.table())
        self._enabled = None

    def enabled(self, enabled: bool = True):
        self ._enabled = enabled

