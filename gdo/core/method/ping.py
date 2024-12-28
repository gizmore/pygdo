from gdo.base.Method import Method


class ping(Method):

    def gdo_trigger(self) -> str:
        return 'ping'

    def gdo_execute(self):
        return self.reply('msg_pong')
