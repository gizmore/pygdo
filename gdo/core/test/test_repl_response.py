import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector


spec = importlib.util.spec_from_file_location('pygdo_repl_response', Path(__file__).resolve().parents[3] / 'bin' / 'pygdo.py')
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class ReplResponseTest(unittest.TestCase):
    def test_ctrl_c_clears_nonempty_input(self):
        event = MagicMock()
        event.current_buffer.text = 'unfinished command'
        cli.repl_key_bindings().bindings[0].handler(event)
        event.current_buffer.reset.assert_called_once_with()
        event.app.exit.assert_not_called()

    def test_ctrl_c_exits_on_empty_input(self):
        event = MagicMock()
        event.current_buffer.text = ''
        cli.repl_key_bindings().bindings[0].handler(event)
        event.current_buffer.reset.assert_not_called()
        event.app.exit.assert_called_once_with(exception=KeyboardInterrupt, style='class:aborting')

    def test_error_top_bar_appears_once_in_cli_and_other_format(self):
        page = MagicMock()
        page._top_bar.render.return_value = 'error'
        result = MagicMock()
        result.render.return_value = ''
        msg = Message('.calc bad', Mode.render_cli)
        with patch('gdo.base.Message.Application.get_page', return_value=page):
            cli.prepare_repl_response(msg, result)
            connector = MagicMock()
            connector.get_render_mode.return_value = Mode.render_cli
            Connector.render_outgoing(connector, msg)
            self.assertEqual('error', msg._result)
            connector.get_render_mode.return_value = Mode.render_html
            Connector.render_outgoing(connector, msg)
            self.assertEqual('error', msg._result)
        self.assertIs(msg._gdt_result, result)

    def test_normal_result_is_preserved(self):
        page = MagicMock()
        page._top_bar.render.return_value = ''
        result = MagicMock()
        result.render.return_value = '42'
        msg = Message('.calc 6*7', Mode.render_cli)
        with patch('gdo.base.Message.Application.get_page', return_value=page):
            cli.prepare_repl_response(msg, result)
        self.assertEqual('42', msg._result)
        self.assertEqual(Mode.render_cli, msg._result_mode)
