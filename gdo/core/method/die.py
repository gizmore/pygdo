import asyncio

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Bool import GDT_Bool


class die(Method):

    def gdo_trigger(self) -> str:
        return 'die'

    def gdo_permission(self):
        return 'admin'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Bool('restart').initial('0'),
        ]

    def is_restart(self) -> bool:
        return self.param_value('restart')

    async def gdo_execute(self):
        if self.is_restart():
            out = self.reply('msg_rebooting')
        else:
            out = self.reply('msg_dying')
        Application.RUNNING = False
        return out
