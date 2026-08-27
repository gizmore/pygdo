import os

from gdo.base.Application import Application
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdotest.TestUtil import GDOTestCase


class RestOfTextTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        Application.init_cli()

    def test_web_form_renders_as_one_textarea(self):
        field = GDT_RestOfText('body').label_raw('Message').not_null()
        field.val(field.to_val(['A', 'complete message']))

        out = field.render_form()

        self.assertIn('<textarea', out)
        self.assertIn('name="body"', out)
        self.assertNotIn('name="body[]"', out)
        self.assertIn('A complete message', out)
        self.assertEqual('A complete message', field.get_value())
