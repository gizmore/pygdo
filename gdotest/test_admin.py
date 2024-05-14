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
        self.assertIn("core", res, "Module Core is not listen in adm.conf")
        res = cli_plug(None, "conf core")
        self.assertIn("send_404_mails", res, "send_404_mails is not listen in adm.conf")
        res = cli_plug(None, "conf core send_404_mails")


if __name__ == '__main__':
    unittest.main()
