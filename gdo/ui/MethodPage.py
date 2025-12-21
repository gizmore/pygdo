from gdo.base.Method import Method
from gdo.core.GDT_Template import GDT_Template


class MethodPage(Method):

    def execute(self):
        return GDT_Template().template(self.gdo_module().get_name(), self.__class__.__name__)
