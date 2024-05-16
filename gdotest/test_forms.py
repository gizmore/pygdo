import os.path
import unittest

from gdo.base.Application import Application
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDT_String import GDT_String
from gdo.base.ModuleLoader import ModuleLoader
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdotest.TestUtil import web_gizmore


class FormTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_forms(self):
        gizmore = web_gizmore()
        Application.set_session(GDO_Session.for_user(gizmore))
        form = GDT_Form()
        form.add_field(GDT_String("login"), GDT_CSRF(), GDT_Submit())
        form.actions().add_field(GDT_Submit())
        tpl = form.render_html()
        self.assertIn('<form', tpl, 'check if form somewhat renders')


if __name__ == '__main__':
    unittest.main()
