import os
import re

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.connector.Web import Web
from gdo.install.Installer import Installer
from gdotest.TestUtil import GDOTestCase, cli_plug


class ConnectAccountTest(GDOTestCase):
    """A connector account joins a master only after its own approval."""

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

        web = Web.get_server()
        bash = GDO_Server.get_by_connector('bash')
        self.master = await web.get_or_create_user('LinkMaster')
        self.slave = await bash.get_or_create_user('LinkSlave')
        self.other = await bash.get_or_create_user('LinkOther')
        for user in (self.master, self.slave, self.other):
            user._authenticated = True
            user.save_val('user_link', None)

    def request_token(self):
        output = cli_plug(self.master, f'$user.connect {self.slave.render_name()}')
        match = re.search(r'\$user\.approve ([0-9]+\.[0-9]+\.[0-9a-f]+\.[0-9]+\.[0-9a-f]{64})', output)
        self.assertIsNotNone(match, output)
        return match.group(1)

    def test_01_connect_requires_the_named_slave_to_approve(self):
        token = self.request_token()
        output = cli_plug(self.other, f'$user.approve {token}')
        self.assertIn('another account', output)
        self.slave.reload()
        self.assertIsNone(self.slave.get_linked_user())

    async def test_02_approval_connects_and_message_keeps_reply_identity(self):
        token = self.request_token()
        output = cli_plug(self.slave, f'$user.approve {token}')
        self.assertIn('connected account', output)
        self.slave.reload()
        self.assertEqual(self.master.get_id(), self.slave.get_linked_user().get_id())
        self.assertEqual(self.master.get_id(), self.slave.get_effective_user().get_id())

        message = Message('$whoami', Mode.render_cli).env_user(self.slave).env_server(
            self.slave.get_server()).env_session(GDO_Session.for_user(self.slave))
        await message.execute()
        self.assertEqual(self.slave.get_id(), message._env_reply_to.get_id())
        self.assertEqual(self.master.get_id(), message._env_user.get_id())

    def test_03_connection_token_cannot_replace_an_existing_link(self):
        token = self.request_token()
        cli_plug(self.slave, f'$user.approve {token}')
        output = cli_plug(self.slave, f'$user.approve {token}')
        self.assertIn('already linked', output)

    def test_04_tampered_token_does_not_connect(self):
        token = self.request_token()
        tampered = token[:-1] + ('0' if token[-1] != '0' else '1')
        output = cli_plug(self.slave, f'$user.approve {tampered}')
        self.assertIn('invalid or has expired', output)
        self.slave.reload()
        self.assertIsNone(self.slave.get_linked_user())
