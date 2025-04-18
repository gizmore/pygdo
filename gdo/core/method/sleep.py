import asyncio

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_None import GDT_None
from gdo.date.GDT_Duration import GDT_Duration


class sleep(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'sleep'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Duration('time').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        await asyncio.sleep(self.param_value('time'))
        return GDT_None()
