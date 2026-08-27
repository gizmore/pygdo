import json
import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_User import GDT_User
from gdo.core.connector.Web import Web
from gdotest.TestUtil import GDOTestCase, web_gizmore, web_plug


class CompletionTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)

    async def test_user_completion_returns_resolvable_user_names(self):
        user = await Web.get_server().get_or_create_user('CompletionTestUser')

        out = web_plug('core.user_completion.json?_lang=en&q=CompletionTest').exec()
        data = json.loads(out)['data']

        self.assertTrue(any(
            item['id'] == user.get_id()
            and item['var'] == user.get_name_sid()
            and item['display_var'] == user.render_name()
            for item in data
        ))

    def test_admin_login_as_uses_user_completion(self):
        web_gizmore()
        out = web_plug('admin.login_as.html?_lang=en').user('gizmore').exec()
        self.assertIn('gdo-completion="/core.user_completion.json', out)

    async def test_user_completion_initial_keeps_the_resolvable_value(self):
        user = await Web.get_server().get_or_create_user('CompletionInitialUser')
        field = GDT_User('user').with_completion().value(user)

        initial = field.gdo_completion_initial()

        self.assertEqual(user.get_id(), initial['id'])
        self.assertEqual(user.get_name_sid(), initial['var'])
        self.assertEqual(user.render_name(), initial['display_var'])

    async def test_user_completion_limits_a_server_suffix(self):
        server = GDO_Server.table().get_by_vals({'serv_name': 'completion-discord'})
        if server is None:
            web = Web.get_server()
            server = GDO_Server.blank({
                'serv_name': 'completion-discord',
                'serv_url': web.gdo_val('serv_url'),
                'serv_trigger': web.gdo_val('serv_trigger'),
                'serv_username': 'CompletionBot',
                'serv_connector': 'web',
                'serv_language': 'en',
                'serv_enabled': '1',
            }).insert()
        user = await server.get_or_create_user('CompletionScopedUser', 'Completion Scoped User')

        out = web_plug('core.user_completion.json?_lang=en&q=CompletionScopedUser{completion-discord}').exec()
        data = json.loads(out)['data']

        self.assertEqual(1, len(data))
        self.assertEqual(user.get_id(), data[0]['id'])
        self.assertEqual(user.get_name_sid(), data[0]['var'])
        self.assertEqual(user.render_name(), data[0]['display_var'])
