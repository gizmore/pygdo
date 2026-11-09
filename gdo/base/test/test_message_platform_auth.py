import unittest
from unittest.mock import MagicMock

from gdo.base.Message import Message
from gdo.base.Render import Mode


class MessagePlatformAuthTest(unittest.TestCase):
    def test_authentication_is_scoped_to_effective_user_copy(self):
        origin = MagicMock()
        effective = MagicMock()
        effective._authenticated = False
        origin.get_effective_user.return_value = effective
        message = Message('hello', Mode.render_txt)
        message._platform_authenticated = True
        result = message.effective_message_user(origin)
        self.assertIsNot(result, effective)
        self.assertTrue(result._authenticated)
        self.assertFalse(effective._authenticated)

    def test_untrusted_message_does_not_authenticate(self):
        origin = MagicMock()
        effective = MagicMock()
        effective._authenticated = False
        origin.get_effective_user.return_value = effective
        message = Message('hello', Mode.render_txt)
        self.assertIs(effective, message.effective_message_user(origin))
        self.assertFalse(effective._authenticated)

    def test_webhook_override_does_not_inherit_cached_auth(self):
        origin = MagicMock()
        effective = MagicMock()
        effective._authenticated = True
        origin.get_effective_user.return_value = effective
        message = Message('hello', Mode.render_txt)
        message._platform_authenticated = False
        result = message.effective_message_user(origin)
        self.assertFalse(result._authenticated)
        self.assertTrue(effective._authenticated)
