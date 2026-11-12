import unittest
from unittest.mock import MagicMock

from gdo.base.Message import Message
from gdo.base.Render import Mode


class MessagePlatformAuthTest(unittest.TestCase):
    def test_platform_identity_requires_a_trusted_positive_integer(self):
        for sender_id, trusted, expected in ((7, True, True), (7, False, False),
                                             (True, True, False), (0, True, False),
                                             ('7', True, False), (None, True, False)):
            with self.subTest(sender_id=sender_id, trusted=trusted):
                message = Message('hello', Mode.render_txt)
                self.assertIs(message, message.platform_identity(sender_id, trusted))
                self.assertEqual(expected, message._platform_authenticated)

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
