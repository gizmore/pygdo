import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.base.ModuleLoader import ModuleLoader
from gdo.ui.GDT_Divider import GDT_Divider
from gdo.ui.GDT_Section import GDT_Section
from gdotest.TestUtil import web_plug


class UITestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_01_template(self):
        s = GDT_String('login')
        tpl = s.render_form()
        self.assertIn("text", tpl, 'Test if string form renders somewhat 1')
        self.assertIn("login", tpl, 'Test if string form renders somewhat 2')

    def test_02_flow(self):
        horz = GDT_Divider().title_raw('Test').horizontal().render_cli()
        self.assertEqual('|', horz[0], 'Divider does not start with pipe')

    def test_03_section(self):
        sect = GDT_Section().title_raw("Test").render_title(Mode.CLI)
        self.assertIn(sect, "Test", 'Section does not render in CLI mode.')

    def test_04_method_errors(self):
        result = web_plug("math.calc.html").post({'submit': '1', 'expression': 'PI()'}).exec()
        self.assertIn('<form', result, 'errorneus page does not render fallback')


if __name__ == '__main__':
    unittest.main()
