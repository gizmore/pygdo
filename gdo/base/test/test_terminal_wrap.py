import unittest

from gdo.base.Util import terminal_wrap


class TerminalWrapTest(unittest.TestCase):

    def test_wraps_at_whitespace(self):
        self.assertEqual('alpha\nbeta\ngamma', terminal_wrap('alpha beta gamma', 6))

    def test_preserves_ansi_and_does_not_count_it(self):
        green = '\x1b[32m'
        reset = '\x1b[0m'
        self.assertEqual(
            f'{green}alpha{reset}\nbeta',
            terminal_wrap(f'{green}alpha{reset} beta', 6),
        )

    def test_preserves_explicit_newlines(self):
        self.assertEqual('alpha\nbeta', terminal_wrap('alpha\nbeta', 20))
