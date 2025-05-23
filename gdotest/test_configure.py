import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.install.Config import Config
from gdotest.TestUtil import GDOTestCase


class ConfigureTestCase(GDOTestCase):
    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()

    def test_01_configure(self):
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        date1 = Application.CONFIG['gen']['date']
        data = Config.data(Application.CONFIG)
        Config.rewrite(Application.file_path('protected/config_test.toml'), data)
        Application.init(Application.PATH)
        date2 = Application.CONFIG['gen']['date']
        self.assertNotEqual(date1, date2, "Cannot rewrite config.")


if __name__ == '__main__':
    unittest.main()
