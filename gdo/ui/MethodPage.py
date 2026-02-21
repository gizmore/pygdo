from typing import Any

from gdo.base.Method import Method
from gdo.core.GDT_Template import GDT_Template


class MethodPage(Method):

    def gdo_page_vars(self) -> dict[str, Any]:
        return self.EMPTY_DICT

    def gdo_execute(self):
        return GDT_Template().template(self.gdo_module().get_name, f'{self.__class__.__name__}.html', self.gdo_page_vars())
