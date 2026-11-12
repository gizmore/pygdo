import unittest
from unittest.mock import MagicMock, patch

from gdo.base.method.server_error import server_error


class TestServerErrorTraceback(unittest.TestCase):
    def test_uses_rich_traceback_without_locals_and_escapes_html(self):
        panel = MagicMock()
        with patch('gdo.base.method.server_error.GDT_Error', return_value=panel), \
                patch('gdo.base.method.server_error.Logger.traceback', return_value='<unsafe>') as render:
            try:
                raise ValueError('failure')
            except ValueError as exception:
                server_error.gdo_execute(None)
                render.assert_called_once_with(exception, show_locals=False)
            panel.text_raw.assert_called_once_with('<pre>&lt;unsafe&gt;</pre>')

    def test_no_active_exception(self):
        panel = MagicMock()
        with patch('gdo.base.method.server_error.GDT_Error', return_value=panel):
            server_error.gdo_execute(None)
        panel.text_raw.assert_called_once_with('Internal server error.')
