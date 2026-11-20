from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.Util import gdo_print
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server
from gdo.base.Application import Application
from gdo.base.Cache import Cache


class Bash(Connector):

    @staticmethod
    def repl_channel(user_id) -> str:
        return f"pygdo:repl:{Application.config('core.env')}:{user_id}"

    def render_user_connect_help(self) -> str:
        return t('help_bash_connector')

    def render_user_command_help(self) -> str:
        return '(gl+hf)'

    def get_render_mode(self) -> Mode:
        return Mode.render_cli

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('bash')

    def gdo_needs_authentication(self) -> bool:
        return False

    async def gdo_send_to_channel(self, msg: Message):
        await self.gdo_send_to_user(msg)

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        #PYPP#START#
        if Application.is_unit_test():
            from gdotest.TestUtil import GDOTestCase
            uid = msg._env_user.get_id()
            if uid not in GDOTestCase.MESSAGES:
                GDOTestCase.MESSAGES[uid] = []
            GDOTestCase.MESSAGES[uid].append(msg._result)
        #PYPP#END#
        # Replies sent by another process need a route back to the active REPL.
        # Direct commands inside the REPL retain their normal local output.
        if (not getattr(Application, 'IS_REPL', False)
                and not getattr(Application, 'IS_LOCAL_CLI_COMMAND', False) and Cache.RCACHE):
            if Cache.RCACHE.publish(self.repl_channel(msg._env_user.get_id()), msg._result):
                return
        gdo_print(msg._result)

    def gdo_handle_message(self, message: Message):
        pass

    async def gdo_connect(self) -> bool:
        Logger.debug("Bash connect...")
        self._connected = True
        return True
