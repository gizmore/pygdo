from gdo.base.GDO_Module import GDO_Module
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Select import GDT_Select


class GDT_Module(GDT_Select):
    _enabled: bool | None

    def __init__(self, name):
        super().__init__(name)
        self._enabled = None
        self.init_choices()

    def gdo_choices(self):
        choices = {}
        for module in ModuleLoader.instance()._cache.values():
            name = module.get_name().lower()
            if self._enabled is True and module.is_enabled():
                choices[name] = module
            elif self._enabled is False and not module.is_enabled():
                choices[name] = module
            else:
                choices[name] = module
        return choices

    def enabled(self, enabled: bool = True):
        self ._enabled = enabled
        return self
