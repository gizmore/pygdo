import time

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Thread import Thread
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_RestOfText import GDT_RestOfText


class die(Method):

    def gdo_trigger(self) -> str:
        return 'die'

    def gdo_permission(self):
        return 'admin'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Bool('restart').initial('0'),
            GDT_RestOfText('message').not_null(),
        ]

    def is_restart(self) -> bool:
        return self.param_value('restart')

    def gdo_execute(self) -> GDT:
        quit_message = self.param_value('message') or 'i play dead!'
        if self.is_restart():
            self.msg('msg_rebooting')
        else:
            self.msg('msg_dying')
        self.send_quit_message(quit_message)
        return self.empty()

    def send_quit_message(self, quit_message: str):
        servers = GDO_Server.table().all()
        for server in servers:
            self.send_quit_to_server(server, quit_message)
        time.sleep(1)
        Application.RUNNING = False
        time.sleep(1)
        Thread.join_all()
        time.sleep(1)

    def send_quit_to_server(self, server: GDO_Server, quit_message: str):
        conn = server.get_connector()
        if conn._connected:
            conn.disconnect(quit_message)

