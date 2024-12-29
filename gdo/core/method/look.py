from gdo.base.GDT import GDT
from gdo.base.Method import Method


class look(Method):

    def gdo_trigger(self) -> str:
        return 'look'

    def gdo_connectors(self) -> str:
        return 'irc,telegram'

    def gdo_in_private(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        channel = self._env_channel
        out = []
        for user in channel._users:
            out.append(user.get_name())
        return self.reply('msg_look', [len(out), channel.render_name(), ', '.join(out)])
