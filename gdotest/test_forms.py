import os.path
import unittest

from gdo.base.Application import Application
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDT_String import GDT_String
from gdo.base.ModuleLoader import ModuleLoader
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.base.GDT import GDT
from gdo.table.MethodTable import MethodTable
from gdotest.TestUtil import web_gizmore, GDOTestCase


class FormTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()

    async def test_forms(self):
        gizmore = web_gizmore()
        Application.set_session(GDO_Session.for_user(gizmore))
        form = GDT_Form()
        form.add_fields(GDT_String("login"), GDT_CSRF(), GDT_Submit())
        form.actions().add_field(GDT_Submit())
        tpl = form.render_html()
        self.assertIn('<form', tpl, 'check if form somewhat renders')

    def test_tables_render_headers_by_default(self):
        self.assertTrue(MethodTable().gdo_render_table_headers())

    def test_tables_render_pagination_by_default(self):
        table = MethodTable()
        self.assertTrue(table.gdo_render_pagination())
        self.assertTrue(table.gdo_render_pagination_top())
        self.assertTrue(table.gdo_render_pagination_bottom())

    def test_table_cells_have_no_class_by_default(self):
        self.assertEqual('', GDT().html_cell_class())


if __name__ == '__main__':
    unittest.main()
