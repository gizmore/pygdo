import unittest
from gdo.core.ChallengeToken import issue, verify


class ChallengeTokenTest(unittest.TestCase):
    def test_round_trip_and_tampering(self):
        key = b'k' * 32
        token = issue(key, 'bj1', 'Player Ω')
        self.assertTrue(verify(key, 'bj1', token))
        self.assertFalse(verify(b'x' * 32, 'bj1', token))
        self.assertFalse(verify(key, 'other', token))
        self.assertFalse(verify(key, 'bj1', token[:-1] + ('0' if token[-1] != '0' else '1')))
        self.assertFalse(verify(key, 'bj1', token + '.extra'))
        self.assertFalse(verify(key, 'bj1', 'bj1.%%.bad'))

    def test_short_secrets_and_empty_subjects_are_rejected(self):
        with self.assertRaises(ValueError):
            issue(b'short', 'bj1', 'player')
        with self.assertRaises(ValueError):
            issue(b'k' * 32, 'bj1', '')
