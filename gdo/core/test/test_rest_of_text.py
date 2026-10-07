from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdotest.TestUtil import GDOTestCase


class RestOfTextTest(GDOTestCase):

    async def asyncSetUp(self):
        Application.IS_TEST = True
        Application.init(os.path.dirname(__file__) + '/../../..')
        await super().asyncSetUp()

    def test_normal_rest_of_text_remains_a_plain_string(self):
        field = GDT_RestOfText('sql')
        field.val(['select', '1'])
        self.assertEqual('select 1', field.get_value())
import os.path

from gdo.base.Application import Application
