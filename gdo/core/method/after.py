import asyncio

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

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Duration('time').not_null(),
            GDT_RestOfText('command').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        await asyncio.sleep(self.param_value('time'))
        Application.MESSAGES.put(Message(" ".join(self.param_val('command')), self._env_mode).env_copy(self))
        return self.empty()
