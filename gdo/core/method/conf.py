from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_String import GDT_String


class conf(Method):

    def gdo_trigger(self) -> str:
        return 'conf'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Enum('scope').not_null(),
            GDT_Method('method'),
            GDT_String('name'),
            GDT_String('value'),
        ]

    def gdo_execute(self):
        scope = self.param_val('scope')
        method = self.param_val('method')

