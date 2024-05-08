import time

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Util import Files
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.date.GDT_Duration import GDT_Duration


class launch(Method):

    def gdo_trigger(self) -> str:
        return 'launch'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Bool('force').not_null().initial('0'),
            GDT_Duration('dog_msleep').not_null().initial('5ms'),
        ]

    def is_forced(self) -> bool:
        return self.param_value('force')

    def sleep_ms(self) -> float:
        return self.param_value('dog_msleep')

    def gdo_execute(self) -> GDT:
        if self.is_forced():
            Files.remove(self.lock_path())
        if self.is_running():
            return self.err('err_dog_already_running')
        Files.touch(self.lock_path(), True)
        self.mainloop()

    def lock_path(self) -> str:
        return Application.file_path('bin/dog.lock')

    def is_running(self):
        return Files.is_file(self.lock_path())

    def mainloop(self):
        Logger.debug("Launching DOG Bot")
        sleep_ms = self.sleep_ms()
        while Application.RUNNING:
            self.mainloop_step_timers()
            self.mainloop_step_servers()
            time.sleep(sleep_ms)

    def mainloop_step_timers(self):
        Application.tick()

    def mainloop_step_servers(self):
        servers = GDO_Server.table().all()
        for server in servers:
            self.mainloop_step_server(server)

    def mainloop_step_server(self, server: GDO_Server):
        conn = server.get_connector()
        if not conn.is_connected():
            self.connect_server(server)

    def connect_server(self, server) -> bool:
        conn = server.get_connector()
        if conn.is_connecting():
            return True
        elif conn.should_connect_now():
            if conn.connect():
                return True
            else:
                conn.connect_failed()
                return False
        return True
