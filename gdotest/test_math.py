import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import install_module, cli_plug


class MathTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        install_module('math')
        loader.init_modules()
        loader.init_cli()

    def test_01_sum(self):
        out = cli_plug(None, "sum 1 2 3 4 5")
        self.assertEqual(out, "15", "Math's Sum command does not work.")
