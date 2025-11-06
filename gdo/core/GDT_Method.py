from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Select import GDT_Select


class GDT_Method(GDT_Select):

    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self.case_s()
        self.maxlen(64)

    def gdo_choices(self):
        back = {}
        back.update(ModuleLoader.instance()._meths)
        back.update(ModuleLoader.instance()._methods)
        return back

    def to_value(self, val: str):
        return ModuleLoader.instance().get_method_type(val) if val else None
