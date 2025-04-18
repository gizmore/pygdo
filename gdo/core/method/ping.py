from gdo.base.GDT import GDT
from gdo.base.Method import Method


class ping(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'ping'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        return self.reply('msg_pong')
