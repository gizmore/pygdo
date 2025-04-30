from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Object import GDT_Object


class server(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'server'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Object('id').table(GDO_Server.table()),
        ]
