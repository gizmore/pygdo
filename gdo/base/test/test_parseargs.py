import unittest

from gdo.base.ParseArgs import ParseArgs


class ParseArgsTest(unittest.TestCase):

    def test_bare_cli_flag_means_true(self):
        args = ParseArgs()
        args.add_cli_part('--force')
        self.assertEqual('1', args.get_val('force'))

    def test_cli_flag_with_value_is_preserved(self):
        args = ParseArgs()
        args.add_cli_part('--force=0')
        self.assertEqual('0', args.get_val('force'))
