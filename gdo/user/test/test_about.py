import unittest

from gdo.user.method.about import about


class AboutTest(unittest.TestCase):

    def test_format_about_flattens_whitespace(self):
        self.assertEqual('Hello from Mira', about.format_about('  Hello\n from\tMira  '))

    def test_format_about_has_a_chat_safe_limit(self):
        self.assertEqual(about.MAX_CHAT_LENGTH, len(about.format_about('x' * 400)))
