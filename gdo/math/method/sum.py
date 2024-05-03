import builtins

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_Repeat import GDT_Repeat


class sum(Method):

    def gdo_trigger(self) -> str:
        return 'sum'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Repeat(GDT_Float('x').not_null()),
        ]

    def gdo_execute(self):
        return GDT_Float('result').initial_value(builtins.sum(self.param_value('x')))
