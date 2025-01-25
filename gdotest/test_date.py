import os.path
import unittest
from datetime import datetime

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.date.GDO_Timezone import GDO_Timezone
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdotest.TestUtil import install_module, GDOTestCase


class DateTestCase(GDOTestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules(True, True)
        Application.init_cli()
        install_module('date')

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
        self.assertAlmostEqual(342621420.0, parsed.timestamp(), 6, 'Berlin DB date with human parse format cannot be parsed. It breaks again on summertime 2025! :)')
        # Display UTC date from berlin date
        displayed = Time.display_datetime_iso('en', parsed, 'short', '---', 'UTC')
        self.assertEqual('11/09/1980 12:37', displayed, 'Berlin Date can be printed as UTC')

    def test_diff(self):
        parsed1 = Time.parse_datetime_iso('en', '11/09/1980 13:37', 'Europe/Berlin', 'parse')
        parsed2 = Time.parse_datetime_iso('en', '11/09/1980 12:37', 'Europe/Berlin', 'parse')
        diff = Time.get_diff_time(parsed1.timestamp(), parsed2.timestamp())
        self.assertAlmostEqual(diff, 3600.0, 1, "Date diff is incorrect.")

    def test_durations(self):
        output = Time.human_to_seconds("5s 120ms")
        self.assertAlmostEqual(output, 5.120, 3, 'human_to_seconds() does not work.')
        reverse = Time.human_duration(output)
        self.assertEqual("5s 120ms", reverse, 'human_duration() does not work.')
        output = Time.human_to_seconds('1ms')
        self.assertAlmostEqual(output, 0.001, 3, 'human_to_seconds() does not work for 1ms.')

    def test_age(self):
        age = Time.get_age_in_years(Time.ONE_YEAR)
        self.assertEqual(age, 1, 'Cannot get age in years.')
        time = Time.get_time(Time.get_date())
        age = Time.get_age_in_years(Application.TIME - time)
        self.assertEqual(age, 0, 'Cannot get zero age in years.')

    def test_value_conversion(self):
        col = GDT_Timestamp('test').val('2023-11-09 14:12:11.123')
        dt = col.get_value()
        self.assertIsInstance(dt, datetime, 'Conversion does not yield an object.')

    def test_tz_cache(self):
        tz1 = GDO_Timezone.get_by_name('UTC')
        tz2 = GDO_Timezone.get_by_name('UTC')
        self.assertEqual(tz1, tz2, "Single Identity cache for TZ broken")

    def test_microseconds(self):
        h = Time.human_duration(0.000499)
        self.assertEqual('0.499ms', h, 'Microseconds do not work.')
        h = GDT_Duration('d').units(2, True).value(0.000499).render()
        self.assertEqual('0.499ms', h, 'Microseconds do not work in GDT_Duration.')
        h = Time.human_duration(0.001499)
        self.assertEqual('1.499ms', h, 'Microseconds do not work #2.')
        h = GDT_Duration('d').units(2, True).value(0.001499).render()
        self.assertEqual('1.499ms', h, 'Microseconds do not work in GDT_Duration #2.')
        h = Time.human_duration(66.000499)
        self.assertEqual('1m 6s', h, 'Microseconds do not work #3.')
        h = GDT_Duration('d').units(2, True).value(66.000499).render()
        self.assertEqual('1m 6s', h, 'Microseconds do not work in GDT_Duration #3.')


if __name__ == '__main__':
    unittest.main()
