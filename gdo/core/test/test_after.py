import queue
import unittest
from unittest.mock import Mock

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.after import after


class AfterTest(unittest.IsolatedAsyncioTestCase):

    async def test_schedules_complete_command_without_blocking(self):
        method = object.__new__(after)
        method._env_http = False
        method._env_mode = Mode.render_cli
        method._env_user = Mock()
        method._env_server = Mock()
        method._env_channel = Mock()
        method._env_channel.get_trigger.return_value = '.'
        method._env_session = Mock()
        method._env_reply_to = method._env_user
        method.param_value = Mock(return_value=10.0)
        method.param_val = Mock(return_value='echo 1')
        result = object()
        method.empty = Mock(return_value=result)

        old_events = getattr(Application, 'EVENTS', None)
        old_messages = Application.MESSAGES
        Application.EVENTS = Mock()
        Application.MESSAGES = queue.Queue()
        try:
            self.assertIs(result, await method.gdo_execute())
            Application.EVENTS.add_timer_async.assert_called_once()
            duration, callback = Application.EVENTS.add_timer_async.call_args.args
            self.assertEqual(10.0, duration)
            self.assertTrue(Application.MESSAGES.empty())

            await callback()

            message = Application.MESSAGES.get_nowait()
            self.assertEqual('.echo 1', message._message)
            self.assertIs(method._env_channel, message._env_channel)
            self.assertIs(method._env_user, message._env_user)
        finally:
            if old_events is None:
                del Application.EVENTS
            else:
                Application.EVENTS = old_events
            Application.MESSAGES = old_messages


if __name__ == '__main__':
    unittest.main()
