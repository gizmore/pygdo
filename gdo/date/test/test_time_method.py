from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.date.method.time import time
from gdotest.TestUtil import GDOTestCase


class TimeMethodTest(GDOTestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_uses_user_timezone_and_reports_timestamp(self):
        method = time()
        method.param_value = MagicMock(return_value=None)
        zone = MagicMock()
        zone.gdo_val.return_value = 'Europe/Berlin'
        method._env_user = MagicMock()
        method._env_user.get_setting_value.return_value = zone
        method._env_user.get_lang_iso.return_value = 'en'
        method.reply = MagicMock()
        with patch('gdo.date.method.time.Time.display_datetime_iso', return_value='formatted') as formatter:
            method.gdo_execute()
        key, args = method.reply.call_args.args
        self.assertEqual('date_time_with_utc', key)
        self.assertEqual(('formatted', 'Europe/Berlin'), args[:2])
        self.assertRegex(args[2], r'^[+-]\d{4}$')
        self.assertEqual('formatted', args[3])
        self.assertGreater(args[4], 0)
        self.assertEqual('Europe/Berlin', formatter.call_args_list[0].args[1].tzinfo.key)
        self.assertEqual('UTC', str(formatter.call_args_list[1].args[1].tzinfo))

    def test_missing_timezone_is_reported(self):
        method = time()
        method.param_value = MagicMock(return_value=None)
        method._env_user = MagicMock()
        method._env_user.get_setting_value.return_value = None
        method.err = MagicMock()
        method.gdo_execute()
        method.err.assert_called_once_with('date_timezone_unavailable')

    def test_selected_user_timezone_uses_caller_language(self):
        method = time()
        caller = MagicMock()
        caller.get_lang_iso.return_value = 'en'
        target = MagicMock()
        target.get_setting_value.return_value.gdo_val.return_value = 'Asia/Tokyo'
        method._env_user = caller
        method.param_value = MagicMock(side_effect=lambda key: target if key == 'user' else None)
        method.reply = MagicMock()
        with patch('gdo.date.method.time.Time.display_datetime_iso', return_value='formatted') as formatter:
            method.gdo_execute()
        self.assertEqual('Asia/Tokyo', method.reply.call_args.args[1][1])
        self.assertEqual('en', formatter.call_args.args[0])
        self.assertEqual('Asia/Tokyo', formatter.call_args_list[0].args[1].tzinfo.key)

    def test_explicit_timezone_overrides_user_timezone(self):
        method = time()
        zone = MagicMock()
        zone.gdo_val.return_value = 'Asia/Tokyo'
        method._env_user = MagicMock()
        method._env_user.get_lang_iso.return_value = 'en'
        method.param_value = MagicMock(side_effect=lambda key: zone if key == 'timezone' else None)
        method.reply = MagicMock()
        with patch('gdo.date.method.time.Time.display_datetime_iso', return_value='formatted'):
            method.gdo_execute()
        method._env_user.get_setting_value.assert_not_called()
        self.assertEqual('Asia/Tokyo', method.reply.call_args.args[1][1])

    def test_utc_is_not_shown_twice(self):
        method = time()
        zone = MagicMock()
        zone.gdo_val.return_value = 'Etc/UTC'
        method._env_user = MagicMock()
        method._env_user.get_setting_value.return_value = zone
        method._env_user.get_lang_iso.return_value = 'en'
        method.param_value = MagicMock(return_value=None)
        method.reply = MagicMock()
        with patch('gdo.date.method.time.Time.display_datetime_iso', return_value='formatted') as formatter:
            method.gdo_execute()
        self.assertEqual('date_time_result', method.reply.call_args.args[0])
        formatter.assert_called_once()
