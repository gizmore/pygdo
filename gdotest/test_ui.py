import os.path
import unittest

from gdo.core.Application import Application
from gdo.core.GDT_String import GDT_String
from gdo.core.ModuleLoader import ModuleLoader


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


if __name__ == '__main__':
    unittest.main()
