import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import cli_plug, reinstall_module, cli_gizmore


class AccountTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        reinstall_module('account')
        ModuleLoader.instance().init_cli()
        return self

    def test_01_settings(self):
        result = cli_plug(None, 'settings')
        self.assertIn('language(en)', result, "settings cmd does not work")

    def test_02_print_setting(self):
        result = cli_plug(None, 'set language')
        self.assertIn('language', result, 'print setting does not work')
        self.assertIn('Your system language', result, 'print setting does not work #2')

    def test_03_set_language(self):
        result = cli_plug(None, 'set language de')
        self.assertIn('setting for language changed', result, "Setting system language does not work #1")
        got = cli_gizmore().get_setting_val('language')
        self.assertEqual(got, 'de', 'Cannot set language to german.')



if __name__ == '__main__':
    unittest.main()
