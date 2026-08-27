import unittest

from gdo.base.Query import Query
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_String import GDT_String
from gdo.form.GDT_Form import GDT_Form


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
