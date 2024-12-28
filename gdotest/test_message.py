import unittest
import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader


class MessageTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()

    def test_01_composition(self):
        GDT_M
        pass


if __name__ == '__main__':
    unittest.main()
