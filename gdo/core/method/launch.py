import asyncio
import os
import signal
import time

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.IPC import IPC
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Util import Files
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.method.die import die
from gdo.date.GDT_Duration import GDT_Duration


class launch(Method):

    SERVERS: list[GDO_Server] = []

    _signaled: bool

    def __init__(self):
        super().__init__()
        self._signaled = False

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'launch'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.ADMIN

    def gdo_connectors(self) -> str:
        return 'bash'

    def gdo_transactional(self) -> bool:
        return False

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Bool('force').not_null().initial('0'),
            GDT_Duration('dog_msleep').not_null().initial('25ms'),
        ]

    def is_forced(self) -> bool:
        return self.param_value('force')

    def sleep_ms(self) -> float:
        return self.param_value('dog_msleep')

    async def gdo_execute(self) -> GDT:
        if self.is_forced():
            Files.remove(self.lock_path())
        if self.is_running():
            return self.err('err_dog_already_running')
        Files.put_contents(self.lock_path(), str(os.getpid()))
        Application.IS_DOG = True
        signal.signal(signal.SIGUSR1, self.handle_sigusr1)
        IPC.send('base.ipc_dogpid')
        await self.mainloop()
        return self.reply('msg_all_done')

    @classmethod
    def lock_path(cls) -> str:
        return Application.file_path('bin/dog.pid')

    def is_running(self):
        return Files.is_file(self.lock_path())

    async def mainloop(self):
        Logger.debug("Launching DOG Bot")
        sleep_ms = self.sleep_ms()
        try:
            self.SERVERS = GDO_Server.table().all('serv_enabled')
            while Application.RUNNING:
                Application.tick()
                if self.tried_connecting():
                    await Application.EVENTS.update_timers(Application.TIME)
                for server in self.SERVERS:
                    self.mainloop_step_server(server)
                await self.mainloop_process_ai()
                if self._signaled:
                    from gdo.base.IPC import IPC
                    self._signaled = False
                    IPC.dog_execute_events()
                await asyncio.sleep(sleep_ms)
        except KeyboardInterrupt as ex:
            die().input('message', 'CTRL-C got pressed!').gdo_execute()
            time.sleep(1)
        finally:
            Files.remove(self.lock_path())

    def handle_sigusr1(self, event: str, args: any):
        self._signaled = True

    def tried_connecting(self):
        return Application.runtime() > 30

    def mainloop_step_server(self, server: GDO_Server):
        if not server._has_loop:
            Logger.debug(f"step server {server.render_name()}")
            server._has_loop = True
            asyncio.create_task(server.loop())

    async def mainloop_process_ai(self):
        while not Application.MESSAGES.empty():
            Application.fresh_page()
            message = Application.MESSAGES.get()
            await message.execute()
