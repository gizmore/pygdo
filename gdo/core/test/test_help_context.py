import unittest
from unittest.mock import Mock

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.help import help


class HelpContextTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_repl_help_without_message(self):
        method = help()
        method.get_trigger = Mock(return_value='snapvid')
        method.show_help_for = Mock(return_value='help output')
        self.assertEqual('help output', method.gdo_execute())
        method.show_help_for.assert_called_once_with('snapvid')

    def test_channel_help_replies_privately(self):
        method = help()
        method._message = Mock()
        method._message._env_channel = object()
        method.get_trigger = Mock(return_value='snapvid')
        method.show_help_for = Mock(return_value='help output')
        self.assertEqual('help output', method.gdo_execute())
        method._message.reply_privately.assert_called_once_with(notice=True)
