import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import install_module, cli_plug


class AdminTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        install_module('admin')
        loader.init_cli()

    def test_01_admin_modules(self):
        res = cli_plug(None, "modules -o name -o prio")
        self.assertIn('Core', res, 'Module core does not show up in cli admin_modules()')

    def test_02_config_list(self):
        res = cli_plug(None, "conf")
        self.assertIn("Core", res, "Module Core is not listen in adm.conf")


if __name__ == '__main__':
    unittest.main()
