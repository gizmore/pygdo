from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Server import GDT_Server
from gdo.core.method.launch import launch


class server(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'server'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Server('server').not_null().positional(),
            GDT_Enum('action').choices({
                'status': 'status',
                'up': 'up',
                'down': 'down',
            }).not_null().initial('status').positional(),
        ]

    def get_server(self) -> GDO_Server:
        return self.param_value('server')

    async def gdo_execute(self) -> GDT:
        server = self.get_server()
        action = self.param_val('action')
        if action == 'up':
            await launch.enable_server(server)
        elif action == 'down':
            await launch.disable_server(server)
        connector = server.get_connector()
        enabled = 'up' if server.gdo_val('serv_enabled') == '1' else 'down'
        connection = 'connected' if connector.is_connected() else 'disconnected'
        return self.reply('msg_server_status', (server.get_name(), enabled, connection))
