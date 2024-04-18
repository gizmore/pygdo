import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core import module_core
from gdo.core.connector.Web import Web


class ModuleConfigTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_module_config(self):
        mod = module_core.instance()
        mod.save_config_val('send_404_mails', '0')
        ModuleLoader.instance().reset()
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        got = mod.get_config_val('send_404_mails')
        self.assertEqual(got, '0', "Check if changed default config is working.")
        mod.save_config_val('send_404_mails', '1')
        got = mod.get_config_val('send_404_mails')
        self.assertEqual(got, '1', "Check if changed back config is working.")

    def test_module_user_config(self):
        web = Web.get_server()
        user = web.get_or_create_user('gizmore')
        user.save_setting('email', '')
        email = user.get_setting_val('email')
        self.assertIsNone(email, "User email is not null")
        user.save_setting('email', 'gizmore@gizmore.org')
        email = user.get_setting_val('email')
        self.assertEqual(email, 'gizmore@gizmore.org', "Cannot save user setting")

    def test_module_user_settings(self):
        pass


if __name__ == '__main__':
    unittest.main()
