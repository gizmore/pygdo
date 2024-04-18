import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.connector.Web import Web
from gdotest.TestUtil import install_module, web_plug, cli_plug


class LoginTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        ModuleLoader.instance().load_modules_db()
        module = install_module('account')
        module = install_module('login')
        ModuleLoader.instance().init_modules()
        user = Web.get_server().get_or_create_user('gizmore')
        module.set_password_for(user, '11111111')
        return self

    def test_set_language(self):
        user = Web.get_server().get_or_create_user('gizmore')
        user.authenticate()
        result = cli_plug(user, 'set language de')
        got = user.get_setting_val('language')
        self.assertEqual(got, 'de', 'Cannot set language to german.')


if __name__ == '__main__':
    unittest.main()
