from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Select import GDT_Select


class GDT_Method(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self):
        triggers = ModuleLoader.instance()._methods.keys()
        as_dict = {key: key for key in triggers}
        return as_dict
