import unittest
from unittest.mock import patch

from gdo.account.method.linked import linked


class LinkedPublicTest(unittest.TestCase):
    def test_linked_accounts_allow_unauthenticated_visitors(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None):
            method = linked()
        self.assertFalse(method.gdo_needs_authentication())
