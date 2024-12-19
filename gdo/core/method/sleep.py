import asyncio
import time

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_None import GDT_None
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Duration import GDT_Duration


class sleep(Method):

    def gdo_trigger(self) -> str:
        return 'sleep'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Duration('time').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        await asyncio.sleep(self.param_value('time'))
        return self.empty()
