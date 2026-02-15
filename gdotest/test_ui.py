import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.base.ModuleLoader import ModuleLoader
from gdo.file.GDT_FileSize import GDT_FileSize
from gdo.ui.GDT_Divider import GDT_Divider
from gdo.ui.GDT_Section import GDT_Section
from gdotest.TestUtil import web_plug, GDOTestCase


class UITestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()

    async def test_01_template(self):
        s = GDT_String('login')
        tpl = s.render_form()
        self.assertIn("text", tpl, 'Test if string form renders somewhat 1')
        self.assertIn("login", tpl, 'Test if string form renders somewhat 2')

    async def test_02_flow(self):
        horz = GDT_Divider().title_raw('Test').horizontal().render_cli()
        self.assertEqual('|', horz[1], 'Divider does not start with pipe')

    async def test_03_section(self):
        sect = GDT_Section().title_raw("Test").render_title(Mode.render_cli)
        self.assertIn(sect, "Test", 'Section does not render in CLI mode.')

    def test_04_method_errors(self):
        result = web_plug("math.calc.html").post({'submit': '1', 'expression': 'XI * 3'}).exec()
        self.assertIn('<form', result, 'erroneous page does not render fallback')

    async def test_05_human_filesize(self):
        self.assertEqual(GDT_FileSize.to_human(1024), '1.00 KB', "human file size 1kb failed")


if __name__ == '__main__':
    unittest.main()
