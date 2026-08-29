import os
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.connector.Bash import Bash
from gdo.core.method.channel_set import channel_set
from gdo.core.method.chan_toggle import chan_toggle
from gdo.core.method.server_set import server_set
from gdo.core.method.add_server import add_server
from gdo.net.GDT_Url import GDT_Url
from gdotest.TestUtil import GDOTestCase


class test_channel_set(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_tcp_can_configure_explicit_irc_channel(self):
        """TCP commands may select #wechall on the wc server by channel syntax."""
        tcp = GDO_Server.table().get_by_vals({'serv_name': 'tcp'})
        if tcp is None:
            bash = Bash.get_server()
            tcp = GDO_Server.blank({
                'serv_name': 'tcp',
                'serv_url': bash.gdo_val('serv_url'),
                'serv_trigger': '$',
                'serv_username': 'tcp',
                'serv_connector': bash.gdo_val('serv_connector'),
                'serv_language': 'en',
                'serv_enabled': '1',
            }).insert()
        wc = GDO_Server.table().get_by_vals({'serv_name': 'wc'})
        if wc is None:
            wc = GDO_Server.blank({
                'serv_name': 'wc',
                'serv_url': tcp.gdo_val('serv_url'),
                'serv_trigger': '$',
                'serv_username': 'mira',
                'serv_connector': tcp.gdo_val('serv_connector'),
                'serv_language': 'en',
                'serv_enabled': '1',
            }).insert()
        wechall = wc.get_or_create_channel('#wechall')
        self.assertEqual([wechall.get_id()], [c.get_id() for c in GDT_Channel('channel').query_gdos('#wechall{wc}')])

        user = await tcp.get_or_create_user('channel_set_tcp_admin')
        await GDO_UserPermission.grant(user, GDO_Permission.STAFF)
        current_channel = tcp.get_or_create_channel('channel_set_tcp_admin', creator=user)
        old_language = wechall.gdo_val('chan_language')
        try:
            Message('', Mode.render_cli).env_user(user, True).env_server(tcp).env_channel(current_channel)
            method = (channel_set().env_user(user, True).env_server(tcp).env_channel(current_channel).
                      env_session(GDO_Session.for_user(user)).env_mode(Mode.render_cli))
            method.input('channel', '#wechall{wc}').input('var_name', 'chan_language').input('new_var_value', 'de')
            await method.execute()
            self.assertEqual('de', wechall.gdo_val('chan_language'))
        finally:
            wechall.save_val('chan_language', old_language)

    def test_short_trigger_is_chan_set(self):
        self.assertEqual('channel.set', channel_set.gdo_trigger())
        self.assertEqual('chan.set', channel_set.gdo_trig())

    async def test_bash_cli_channel_mode_can_be_toggled(self):
        user = await Bash.get_server().get_or_create_user('channel_toggle_user')
        channel = Bash.get_server().get_or_create_channel('channel_toggle_user')
        method = (chan_toggle().env_user(user).env_server(Bash.get_server()).env_channel(channel).
                  env_session(GDO_Session.for_user(user)).input('enabled', '0'))
        await method.execute()
        self.assertFalse(Application.STORAGE.cli_channel_mode)

        method = (chan_toggle().env_user(user).env_server(Bash.get_server()).env_channel(channel).
                  env_session(GDO_Session.for_user(user)).input('enabled', '1'))
        await method.execute()
        self.assertTrue(Application.STORAGE.cli_channel_mode)

    def test_connector_setting_renders_its_persisted_name(self):
        self.assertEqual('irc', GDT_Connector('serv_connector').val('irc').render_val())

    def test_server_default_current_resolves_an_empty_option(self):
        server = GDO_Server.table().select().first().exec().fetch_object()
        Message('', Mode.render_cli).env_server(server)
        self.assertEqual(server, GDT_Server('server').default_current().get_value())

    def test_server_set_keeps_the_server_as_an_optional_named_parameter(self):
        parameters = server_set().parameters()
        self.assertFalse(parameters['server'].is_positional())
        self.assertTrue(parameters['var_name'].is_positional())

    def test_add_server_uses_a_tcp_only_reachability_check(self):
        self.assertTrue(add_server().parameters()['url']._url_reachable)
        url = GDT_Url('url').all_schemes().in_and_external().reachable()
        with patch('gdo.net.GDT_Url.socket.create_connection') as connect:
            self.assertTrue(url.validate('ircs://irc.overthewire.org:6697'))
        connect.assert_called_once_with(('irc.overthewire.org', 6697), timeout=5)
