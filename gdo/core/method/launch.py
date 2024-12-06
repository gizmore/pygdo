import asyncio
import functools
import queue
import time

from gdo.base.Application import Application
from gdo.base.Events import Events
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Thread import Thread
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
            GDT_Duration('dog_msleep').not_null().initial('250ms'),
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
        try:
            asyncio.run(self.mainloop())
        except KeyboardInterrupt as ex:
            self.send_quit_message('CTRL-C got pressed')
            raise ex
        return self.reply('msg_all_done')

    def send_quit_message(self, quit_message: str):
        Application.RUNNING = False
        servers = GDO_Server.table().all()
        for server in servers:
            server.get_connector().gdo_disconnect(quit_message)
        Thread.join_all()

    def lock_path(self) -> str:
        return Application.file_path('bin/dog.lock')

    def is_running(self):
        return Files.is_file(self.lock_path())

    async def mainloop(self):
        Logger.debug("Launching DOG Bot")
        sleep_ms = self.sleep_ms()
        try:
            while Application.RUNNING:
                Application.tick()
                servers = GDO_Server.table().all()
                for server in servers:
                    self.mainloop_step_server(server)
                await self.mainloop_process_ai()
                await asyncio.sleep(sleep_ms)
        except Exception as ex:
            raise ex
        finally:
            Files.remove(self.lock_path())

    def mainloop_step_server(self, server: GDO_Server):
        if not server._has_loop:
            Logger.debug(f"step server {server.render_name()}")
            server._has_loop = True
            asyncio.create_task(server.loop())

    def connect_server(self, server) -> bool:
        conn = server.get_connector()
        if conn.is_connecting():
            return True
        elif conn.should_connect_now():
            conn.connect()
        return True

    async def mainloop_process_ai(self):
        try:
            if message := Application.MESSAGES.get(block=False):
                Application.tick()
                Application.fresh_page()
                await message.execute()
        except queue.Empty:
            pass
