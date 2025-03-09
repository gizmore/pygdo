import asyncio

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.date.GDT_Duration import GDT_Duration


class after(Method):

    def gdo_trigger(self) -> str:
        return 'in'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Duration('time'),
            GDT_RestOfText('command'),
        ]

    async def gdo_execute(self) -> GDT:
        await asyncio.sleep(self.param_value('time'))
        Application.MESSAGES.put(Message(self.param_val('command'), self._env_mode).env_copy(self))
        return self.empty()
