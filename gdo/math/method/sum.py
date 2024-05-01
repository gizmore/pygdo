import builtins

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String


class sum(Method):

    def cli_trigger(self) -> str:
        return 'sum'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Repeat().proxy(GDT_Int('x')).not_null(),
        ]

    def gdo_execute(self):
        numbers = self.param_value('x')
        sum_ = builtins.sum(numbers)
        return GDT_String('result').initial(str(sum_))
