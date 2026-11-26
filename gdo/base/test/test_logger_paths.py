import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Logger import Logger


class LoggerPathTest(unittest.TestCase):
    def test_display_name_is_safe_and_user_id_disambiguates(self):
        user = MagicMock()
        user.get_displayname.return_value = '../Mira / Sparkles'
        user.get_id.return_value = 123
        user.get_server.return_value.get_name.return_value = 'Telegram'
        with patch.object(Logger, '_base', '/logs/', create=True):
            self.assertEqual('/logs/Telegram/Mira_Sparkles-123/', Logger.user_log_dir(user))
            user.get_id.return_value = 124
            self.assertEqual('/logs/Telegram/Mira_Sparkles-124/', Logger.user_log_dir(user))


def test_invalid_id_cannot_escape_user_log_directory(monkeypatch):
    import pytest

    user = MagicMock()
    user.get_displayname.return_value = 'Mira'
    user.get_id.return_value = '../other'
    monkeypatch.setattr(Logger, '_base', '/logs/', raising=False)
    with pytest.raises(ValueError):
        Logger.user_log_dir(user)
