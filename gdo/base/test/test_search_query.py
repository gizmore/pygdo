import unittest

from gdo.base.Query import Query
from gdo.base.GDOSorter import GDOSorter
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_String import GDT_String
from gdo.form.GDT_Form import GDT_Form
from gdo.table.GDT_Filter import GDT_Filter


class SearchRow:

    def __init__(self, values: dict[str, str]):
        self.values = values

    def gdo_val(self, name: str):
        return self.values.get(name)


class SearchQueryTest(unittest.TestCase):

    def test_search_terms_are_grouped_after_existing_filters(self):
        query = Query().where('pm_owner=5')
        GDT_String('pm_title').gdo_search_query(query, 'hello')
        GDT_Int('pm_id').gdo_search_query(query, '42')
        query.apply_search_wheres()
        self.assertEqual(
            "(pm_owner=5) AND (pm_title LIKE '%hello%' OR pm_id=42)",
            query._where)

    def test_secret_string_is_not_searchable(self):
        query = Query()
        GDT_String('user_password').secret().gdo_search_query(query, 'secret')
        query.apply_search_wheres()
        self.assertEqual('', query._where)

    def test_float_search_uses_entered_decimal_precision(self):
        query = Query()
        GDT_Float('price').gdo_search_query(query, '1.20')
        query.apply_search_wheres()
        self.assertEqual('(ROUND(price,2)=ROUND(1.2,2))', query._where)

    def test_search_forms_use_get(self):
        self.assertEqual('GET', GDT_Form().get()._http_method)

    def test_in_memory_search_matches_field_semantics(self):
        row = SearchRow({'name': 'Shadowdogs DOCS', 'id': '42', 'price': '1.204'})
        self.assertTrue(GDT_String('name').gdo_search_gdo(row, 'docs'))
        self.assertTrue(GDT_Int('id').gdo_search_gdo(row, '42'))
        self.assertFalse(GDT_Int('id').gdo_search_gdo(row, '2'))
        self.assertTrue(GDT_Float('price').gdo_search_gdo(row, '1.20'))

    def test_in_memory_filter_matches_text_case_insensitively(self):
        result = GDOSorter.filter(
            [SearchRow({'file_name': 'DOCS.md'})],
            GDT_Filter('f').val({'file_name': ['do']}))
        self.assertEqual(1, len(result))
