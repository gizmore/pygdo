from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.net.GDT_Url import GDT_Url


class proxy(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Url('_url').not_null(),
        ]

    def gdo_execute(self):
        pass
