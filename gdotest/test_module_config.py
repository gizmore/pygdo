import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core import module_core


class ModuleConfigTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
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


if __name__ == '__main__':
    unittest.main()
