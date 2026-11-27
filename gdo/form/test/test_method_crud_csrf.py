from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodCrud import MethodCrud
from gdotest.TestUtil import GDOTestCase


class ExampleCrud(MethodCrud):
    def gdo_table(self):
        return MagicMock()

    def crud_gdo(self):
        return None

    def gdo_form_fields(self, gdo):
        return []


class MethodCrudCsrfTest(GDOTestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_http_form_rejects_missing_token_and_accepts_valid_token(self):
        user = MagicMock()
        user.is_authenticated.return_value = True
        with patch.object(Application, 'IS_HTTP', True), \
                patch.object(Application, 'is_unit_test', return_value=False), \
                patch('gdo.form.GDT_CSRF.GDO_User.current', return_value=user), \
                patch('gdo.form.GDT_CSRF.Cache.get', return_value=['valid']), \
                patch('gdo.form.GDT_CSRF.Cache.set'):
            form = GDT_Form()
            ExampleCrud().gdo_create_form(form)
            csrf = form.get_field('csrf')
            self.assertIsNotNone(csrf)
            self.assertFalse(form.validate(None))
            form = GDT_Form()
            ExampleCrud().gdo_create_form(form)
            form.get_field('csrf').val('valid')
            self.assertTrue(form.validate(None))

    def test_non_http_form_does_not_require_token(self):
        with patch.object(Application, 'IS_HTTP', False):
            form = GDT_Form()
            ExampleCrud().gdo_create_form(form)
            self.assertIsNone(form.get_field('csrf'))
