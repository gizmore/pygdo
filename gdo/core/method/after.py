from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.date.GDT_Duration import GDT_Duration


class after(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'in'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Duration('time').not_null(),
            GDT_RestOfText('command').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        duration = self.param_value('time')
        command = self.param_val('command')
        trigger = self._env_channel.get_trigger() if self._env_channel else self._env_server.get_trigger()
        message = Message(f'{trigger}{command}', self._env_mode).env_copy(self)

        async def enqueue():
            Application.MESSAGES.put(message)

        Application.EVENTS.add_timer_async(duration, enqueue)
        return self.empty()
