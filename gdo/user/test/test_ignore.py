import os

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDO_Server import GDO_Server
from gdo.install.Installer import Installer
from gdotest.TestUtil import GDOTestCase


class IgnoreUserTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        Installer.migrate_user_settings()
        loader.init_cli()
        self.server = GDO_Server.get_by_connector('bash')
        self.user = await self.server.get_or_create_user('IgnoredService')

    async def test_ignored_connector_user_skips_new_message_consumers(self):
        seen = []

        async def on_message(message):
            seen.append(message)

        Application.EVENTS.subscribe('new_message', on_message)
        self.user.save_setting('ignore', '1')
        message = Message('startup notice', Mode.render_cli).env_user(self.user).env_server(self.server)
        await message.execute()
        self.assertEqual([], seen)

        self.user.save_setting('ignore', '0')
        message = Message('ordinary message', Mode.render_cli).env_user(self.user).env_server(self.server)
        await message.execute()
        self.assertEqual(1, len(seen))
