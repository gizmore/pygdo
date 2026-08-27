import unittest

from gdo.base.Query import Query
from gdo.date.GDT_Date import GDT_Date
from gdo.date.GDT_Time import GDT_Time
from gdo.date.GDT_Timestamp import GDT_Timestamp


class DateFilterTest(unittest.TestCase):

    def test_timestamp_rejects_an_empty_fraction_without_a_date(self):
        field = GDT_Timestamp('deleted').val('.000')
        self.assertIsNone(field.get_val())
        self.assertEqual('---', field.render_format())

    def test_timestamp_range_combines_date_and_time(self):
        query = Query()
        GDT_Timestamp('created').val({
            'date_from': '2026-08-01', 'time_from': '09:30',
            'date_to': '2026-08-02', 'time_to': '10:00',
        }).gdo_filter_query(None, query)
        self.assertEqual(
            "(created>='2026-08-01 09:30:00') AND (created<='2026-08-02 10:00:59.999')",
            query._where)

    def test_single_timestamp_date_means_whole_day(self):
        query = Query()
        GDT_Timestamp('created').val({'date_from': '2026-08-25'}).gdo_filter_query(None, query)
        self.assertEqual(
            "(created>='2026-08-25 00:00:00') AND (created<='2026-08-25 23:59:59.999')",
            query._where)

    def test_date_filter_ignores_time_values(self):
        query = Query()
        GDT_Date('birthday').val({'date_from': '1980-01-01', 'time_from': '09:30'}).gdo_filter_query(None, query)
        self.assertEqual("(birthday='1980-01-01')", query._where)

    def test_date_filter_uses_between_for_two_dates(self):
        query = Query()
        GDT_Date('birthday').val({'date_from': '1980-01-01', 'date_to': '1980-12-31'}).gdo_filter_query(None, query)
        self.assertEqual("(birthday BETWEEN '1980-01-01' AND '1980-12-31')", query._where)

    def test_time_filter_ignores_date_values(self):
        query = Query()
        GDT_Time('opening').val({'date_from': '2026-01-01', 'time_to': '18:00'}).gdo_filter_query(None, query)
        self.assertEqual("(opening<='18:00:59.999')", query._where)
