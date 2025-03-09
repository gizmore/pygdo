from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server


class Bash(Connector):

    def get_render_mode(self) -> Mode:
        return Mode.CLI

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('bash')

    def gdo_needs_authentication(self) -> bool:
        return False

    async def gdo_send_to_channel(self, msg: Message):
        print(msg._result)

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        print(msg._result)

    def gdo_handle_message(self, message: Message):
        pass

    def gdo_connect(self) -> bool:
        # Logger.debug("Bash connect...")
        self._connected = True
        return True

