from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.net.GDT_Host import GDT_Host
from gdo.net.GDT_Port import GDT_Port


class module_net(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 15

    def gdo_init(self):
        from gdo.core.Connector import Connector
        from gdo.net.connector.TCP import TCP
        Connector.register(TCP)

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Host('host').not_null().initial('0.0.0.0'),
            GDT_Port('port').not_null().initial('6121'),
        ]

    def cfg_host(self) -> str:
        return self.get_config_val('host')

    def cfg_port(self) -> int:
        return self.get_config_value('port')
