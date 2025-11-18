import os
from urllib.parse import parse_qs

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.ParseArgs import ParseArgs
from gdo.core.method.echo import echo
from gdotest.TestUtil import GDOTestCase


class test_argparser(GDOTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)

    async def test_01_cli(self):
        parser = ParseArgs()
        parser.add_cli_line("$echo 1 $(echo 2)")
        method = parser.get_method()
        self.assertIsInstance(method, echo, 'cli parsing failed.')
        self.assertEqual('1 2', method.gdo_execute().render_txt(), 'Nested echo no work')

    async def test_02_path_web(self):
        parser = ParseArgs()
        parser.add_path_vars('/core.echo.html')
        method = parser.get_method()
        self.assertIsInstance(method, echo, 'web path parsing failed.')

    async def test_02_get_web(self):
        parser = ParseArgs()
        parser.add_path_vars('/core.echo.html')
        qs = parse_qs('lst=2&lst=3&arg2=4')
        parser.add_get_vars(qs)
        method = parser.get_method()
        self.assertIsInstance(method, echo, 'web path parsing failed.')
        self.assertEqual(['2', '3'], parser.get_val('lst'), 'web path get parsing failed #1')
        self.assertEqual(['4'], parser.get_val('arg2'), 'web path get parsing failed #2')
