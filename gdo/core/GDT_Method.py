from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Select import GDT_Select


class GDT_Method(GDT_Select):

    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self.case_s()
        self.maxlen(64)

    def gdo_choices(self):
        triggers = ModuleLoader.instance()._methods.keys()
        return {key: key for key in triggers}

    def to_value(self, val: str):
        return ModuleLoader.instance().get_method(val) if val else None
