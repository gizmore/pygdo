import unittest
from unittest.mock import patch

from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time


class TimestampCardLiveTest(unittest.TestCase):
    def test_minute_datetime_with_past_or_future_relative_time(self):
        with patch('gdo.ui.WithIcon.t', side_effect=lambda key: key):
            field = GDT_Timestamp('created').val('2026-11-20 12:00:00')
        with patch.object(Time, 'display_date', return_value='11/20/2026 12:00'), \
             patch.object(Time, 'human_duration', return_value='1h'), \
             patch('gdo.date.GDT_Timestamp.t', side_effect=lambda key, args: f'{key}:{args[0]}'):
            for delta, expected in ((3600, 'date_relative_past:1h'), (-3600, 'date_relative_future:1h')):
                with self.subTest(delta=delta), patch.object(Time, 'get_time_ago', return_value=delta):
                    self.assertEqual(f'11/20/2026 12:00 ({expected})', field.render_format(Time.FMT_BOTH_MINUTE))

    def test_card_contains_live_age_and_full_date(self):
        with patch('gdo.ui.WithIcon.t', side_effect=lambda key: key):
            field = GDT_Timestamp('created').val('2026-11-20 12:00:00')
        with patch.object(field, 'render_card_label', return_value='Created'), \
             patch.object(Time, 'display_date', return_value='Full date'), \
             patch.object(Time, 'get_time', return_value=12345), \
             patch.object(Time, 'get_time_ago', return_value=25), \
             patch.object(Time, 'human_duration', return_value='25s'):
            rendered = field.render_card()
        self.assertIn('Full date', rendered)
        self.assertIn('class="ago"', rendered)
        self.assertIn('gdo-ts="12345"', rendered)
        self.assertIn('>25s</span>', rendered)


if __name__ == '__main__':
    unittest.main()
