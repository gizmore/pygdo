from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Select import GDT_Select


class GDT_Module(GDT_Select):

    _enabled: bool|None

    def __init__(self, name: str):
        super().__init__(name)
        self._enabled = None
        # self.init_choices()

    def gdo_choices(self):
        choices = {}
        for name, module in ModuleLoader.instance()._cache.items():
            if ((self._enabled is True and module.is_enabled()) or
                (self._enabled is False and not module.is_enabled()) or
                (self._enabled is None)):
                choices[name] = module
        return choices

    def enabled(self, enabled: bool|None = True):
        self ._enabled = enabled
        return self
