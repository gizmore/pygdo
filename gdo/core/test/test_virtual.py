import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Query import Query
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_Virtual import GDT_Virtual


class VirtualTest(unittest.TestCase):
    def setUp(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None):
            self.field = GDT_Virtual(GDT_UInt('number')).query(Query().raw('SELECT 7'))

    def test_manual_is_default(self):
        query = Query().table('example').select()
        self.field.gdo_before_select(MagicMock(), query)
        self.assertNotIn('AS number', query.build_query())
        self.assertIs(query, self.field.select_into(query))
        self.assertIn('( SELECT 7 ) AS number', query.build_query())

    def test_auto_select_can_be_enabled_and_disabled(self):
        self.field.auto_select()
        query = Query().table('example').select()
        self.field.gdo_before_select(MagicMock(), query)
        self.assertIn('( SELECT 7 ) AS number', query.build_query())
        self.field.auto_select(False)
        query = Query().table('example').select()
        self.field.gdo_before_select(MagicMock(), query)
        self.assertNotIn('AS number', query.build_query())

    def test_missing_query_is_reported(self):
        self.field._query = None
        with self.assertRaises(ValueError):
            self.field.select_into(Query().select())
