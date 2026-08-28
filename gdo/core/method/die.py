import asyncio

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_RestOfText import GDT_RestOfText


class die(Method):
    """
    Make a bot die.
    """
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'die'

    def gdo_permission(self):
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Bool('restart').initial('0'),
            GDT_RestOfText('message'),
        ]

    def is_restart(self) -> bool:
        return self.param_value('restart')

    async def gdo_execute(self) -> GDT:
        quit_message = self.param_value('message') or 'i play dead!'
        if self.is_restart():
            self.msg('msg_rebooting')
            Application.RESTARTING = True
        else:
            self.msg('msg_dying')
        await self.send_quit_message(quit_message)
        return self.empty()

    async def send_quit_message(self, quit_message: str):
        servers = GDO_Server.table().all()
        # Stop server loops before closing transports.  Otherwise a connector
        # that notices its own disconnect can schedule one final reconnect.
        Application.RUNNING = False
        await asyncio.gather(
            *(self.send_quit_to_server(server, quit_message) for server in servers),
            return_exceptions=True,
        )

    async def send_quit_to_server(self, server: GDO_Server, quit_message: str):
        conn = server.get_connector()
        if conn._connected:
            await conn.disconnect(quit_message)
