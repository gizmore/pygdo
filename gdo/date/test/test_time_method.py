import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.date.method.time import time


class TimeMethodTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_uses_user_timezone_and_reports_timestamp(self):
        method = time()
        zone = MagicMock()
        zone.gdo_val.return_value = 'Europe/Berlin'
        method._env_user = MagicMock()
        method._env_user.get_setting_value.return_value = zone
        method._env_user.get_lang_iso.return_value = 'en'
        method.reply = MagicMock()
        with patch('gdo.date.method.time.Time.display_datetime_iso', return_value='formatted') as formatter:
            method.gdo_execute()
        key, args = method.reply.call_args.args
        self.assertEqual('date_time_result', key)
        self.assertEqual(('formatted', 'Europe/Berlin'), args[:2])
        self.assertRegex(args[2], r'^[+-]\d{4}$')
        self.assertGreater(args[3], 0)
        self.assertEqual('Europe/Berlin', formatter.call_args.args[1].tzinfo.key)

    def test_missing_timezone_is_reported(self):
        method = time()
        method._env_user = MagicMock()
        method._env_user.get_setting_value.return_value = None
        method.err = MagicMock()
        method.gdo_execute()
        method.err.assert_called_once_with('date_timezone_unavailable')
