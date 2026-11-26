import unittest
from unittest.mock import Mock, patch

from gdo.core.connector.Bash import Bash


class BashNoticeTest(unittest.IsolatedAsyncioTestCase):
    async def test_remote_notice_without_repl_uses_wall(self):
        message = Mock()
        message._result = 'notice text'
        with patch('gdo.core.connector.Bash.Application.is_unit_test', return_value=False), \
                patch('gdo.core.connector.Bash.Cache.RCACHE', None), \
                patch('gdo.core.connector.Bash.Application.IS_REPL', False, create=True), \
                patch('gdo.core.connector.Bash.Application.IS_LOCAL_CLI_COMMAND', False, create=True), \
                patch('gdo.core.connector.Bash.subprocess.run') as wall, \
                patch('gdo.core.connector.Bash.gdo_print') as output:
            await Bash().gdo_send_to_user(message, notice=True)
        wall.assert_called_once_with(['wall'], input='notice text', text=True, check=True, timeout=5)
        output.assert_not_called()

    async def test_remote_reply_publishes_to_target_repl(self):
        message = Mock()
        message._result = 'hello'
        message._env_user.get_id.return_value = 42
        redis = Mock()
        redis.publish.return_value = 1
        with patch('gdo.core.connector.Bash.Application.is_unit_test', return_value=False), \
                patch('gdo.core.connector.Bash.Application.IS_REPL', False, create=True), \
                patch('gdo.core.connector.Bash.Application.IS_LOCAL_CLI_COMMAND', False, create=True), \
                patch('gdo.core.connector.Bash.Application.config', return_value='test'), \
                patch('gdo.core.connector.Bash.Cache.RCACHE', redis), \
                patch('gdo.core.connector.Bash.gdo_print') as output:
            await Bash().gdo_send_to_user(message)
        redis.publish.assert_called_once_with('pygdo:repl:test:42', 'hello')
        output.assert_not_called()

    async def test_local_command_stays_in_own_terminal(self):
        message = Mock()
        message._result = 'local result'
        redis = Mock()
        with patch('gdo.core.connector.Bash.Application.is_unit_test', return_value=False), \
                patch('gdo.core.connector.Bash.Application.IS_LOCAL_CLI_COMMAND', True, create=True), \
                patch('gdo.core.connector.Bash.Cache.RCACHE', redis), \
                patch('gdo.core.connector.Bash.gdo_print') as output:
            await Bash().gdo_send_to_user(message)
        redis.publish.assert_not_called()
        output.assert_called_once_with('local result')

    async def test_wall_failure_falls_back_to_local_output(self):
        message = Mock()
        message._result = 'notice text'
        with patch('gdo.core.connector.Bash.Application.is_unit_test', return_value=False), \
                patch('gdo.core.connector.Bash.Application.IS_REPL', False, create=True), \
                patch('gdo.core.connector.Bash.Application.IS_LOCAL_CLI_COMMAND', False, create=True), \
                patch('gdo.core.connector.Bash.Cache.RCACHE', None), \
                patch('gdo.core.connector.Bash.subprocess.run', side_effect=OSError('unavailable')), \
                patch('gdo.core.connector.Bash.Logger.warning'), \
                patch('gdo.core.connector.Bash.gdo_print') as output:
            await Bash().gdo_send_to_user(message)
        output.assert_called_once_with('notice text')
