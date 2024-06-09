from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server


class Bash(Connector):

    def get_render_mode(self) -> Mode:
        return Mode.CLI

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('Bash')

    def gdo_needs_authentication(self) -> bool:
        return False

    async def gdo_send_to_user(self, msg: Message):
        print(msg._result)
