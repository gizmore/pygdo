from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Server import GDT_Server
from gdo.net.GDT_Url import GDT_Url
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
                'set': 'set',
            }).not_null().initial('status').positional(),
            GDT_Enum('column').choices({
                'serv_url': 'serv_url',
            }).not_null().positional(),
            GDT_Url('var').schemes(['tcp', 'tcps']).in_and_external().not_null().positional(),
        ]

    async def gdo_execute(self) -> GDT:
        server = self.param_value('server')
        action = self.param_val('action')
        if action == 'up':
            await launch.enable_server(server)
        elif action == 'down':
            await launch.disable_server(server)
        elif action == 'set':
            column = self.param_val('column')
            value = self.param_val('var')
            server.save_val(column, value)
            return self.reply('msg_server_set', (server.get_name(), column, value))
        connector = server.get_connector()
        enabled = 'up' if server.gdo_val('serv_enabled') == '1' else 'down'
        connection = 'connected' if connector.is_connected() else 'disconnected'
        return self.reply('msg_server_status', (server.get_name(), enabled, connection))
