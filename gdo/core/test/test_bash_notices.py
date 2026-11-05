import unittest
from unittest.mock import Mock, patch

from gdo.core.connector.Bash import Bash


class BashNoticeTest(unittest.IsolatedAsyncioTestCase):
    async def test_notice_is_printed_to_current_process(self):
        message = Mock()
        message._result = 'notice text'
        with patch('gdo.core.connector.Bash.Application.is_unit_test', return_value=False), \
                patch('gdo.core.connector.Bash.gdo_print') as output:
            await Bash().gdo_send_to_user(message, notice=True)
        output.assert_called_once_with('notice text')
