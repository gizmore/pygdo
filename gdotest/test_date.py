import os.path
import re
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.date.GDO_Timezone import GDO_Timezone
from gdo.date.Time import Time
from gdotest.TestUtil import install_module


class DateTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        install_module('date')
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_installed(self):
        self.assertEqual(Time.UTC, '1', "test if UTC is timezone 1")

    def test_all_installed(self):
        self.assertGreater(GDO_Timezone.table().count_where(), 250, 'Some timezones were installed.')

    def test_db_date_is_ok(self):
        date = Time.get_date()
        self.assertIsNotNone(date, 'Test if date returns something.')
        self.assertEqual(date[0:10], Time.get_date_without_time(), "Test if date and date without time match.")
        self.assertEqual(Time.get_date(0, '%Y-%H'), '1970-00', 'Test if UTC works')

    def test_db_parser(self):
        # Baseline and 0 test.
        parsed = Time.parse_datetime_iso('en', '1970-01-01 00:00:00.000000', 'UTC', 'db')
        self.assertEqual(0, parsed.timestamp(), 'UTC DB date can be parsed.')
        # DB Parser micros
        parsed = Time.parse_datetime_iso('en', '1980-11-09 16:20:42.313375', 'UTC', 'db')
        self.assertAlmostEqual(342634842.313375, parsed.timestamp(), 6, 'UTC DB date with micros cannot be parsed.')

    def test_tz_and_display(self):
        # TZ Parser human
        parsed = Time.parse_datetime_iso('en', '11/09/1980 13:37', 'Europe/Berlin', 'parse')
        self.assertAlmostEqual(342617820.0, parsed.timestamp(), 6, 'Berlin DB date with human parse format cannot be parsed.')
        # Display UTC date from berlin date
        displayed = Time.display_datetime_iso('en', parsed, 'short', '---', 'UTC')
        self.assertEqual('11/09/1980 11:37', displayed, 'Berlin Date can be printed as UTC')

    def test_diff(self):
        parsed1 = Time.parse_datetime_iso('en', '11/09/1980 13:37', 'Europe/Berlin', 'parse')
        parsed2 = Time.parse_datetime_iso('en', '11/09/1980 12:37', 'Europe/Berlin', 'parse')
        diff = Time.get_diff_time(parsed1.timestamp(), parsed2.timestamp())
        self.assertAlmostEqual(diff, 3600.0, 1, "Date diff is incorrect.")


if __name__ == '__main__':
    unittest.main()
