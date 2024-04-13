import os.path
import unittest

from gdo.base.Application import Application
from gdo.core.GDT_String import GDT_String
from gdo.base.ModuleLoader import ModuleLoader
from gdo.ui.GDT_Divider import GDT_Divider


class UITestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_template(self):
        s = GDT_String('login')
        tpl = s.render_form()
        self.assertIn("text", tpl, 'Test if string form renders somewhat 1')
        self.assertIn("login", tpl, 'Test if string form renders somewhat 2')

    def test_flow(self):
        horz = GDT_Divider().title_raw('Test').horz().render_cli()
        self.assertEqual('|', horz[0], 'Divider does not start with pipe')


        self.assertEqual(horz, '|', "Render for horz() Divider failed-")


if __name__ == '__main__':
    unittest.main()
