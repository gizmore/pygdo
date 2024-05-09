import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import cli_plug, get_gizmore, reinstall_module


class AccountTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        reinstall_module('account')
        ModuleLoader.instance().init_cli()
        return self

    def test_set_language(self):
        # user = Web.get_server().get_or_create_user('gizmore')
        # user.authenticate()
        result = cli_plug(None, 'set language de')
        got = get_gizmore().get_setting_val('language')
        self.assertEqual(got, 'de', 'Cannot set language to german.')


if __name__ == '__main__':
    unittest.main()
