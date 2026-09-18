import unittest

from gdo.base.ParseArgs import ParseArgs
from gdo.base.Parser import Parser


class _FakeMethod:

    def __init__(self):
        self._raw_args = ParseArgs()


class ParseArgsTest(unittest.TestCase):

    def test_bare_cli_flag_means_true(self):
        args = ParseArgs()
        args.add_cli_part('--force')
        self.assertEqual('1', args.get_val('force'))

    def test_cli_flag_with_value_is_preserved(self):
        args = ParseArgs()
        args.add_cli_part('--force=0')
        self.assertEqual('0', args.get_val('force'))

    def test_single_dash_option_consumes_following_value(self):
        args = ParseArgs()
        args.add_cli_line(['-s', 'foo'])
        self.assertEqual('foo', args.get_val('s'))

    def test_double_dash_option_consumes_following_value(self):
        args = ParseArgs()
        args.add_cli_line(['--search', 'foo'])
        self.assertEqual('foo', args.get_val('search'))

    def test_negative_number_stays_positional(self):
        args = ParseArgs()
        args.add_cli_line(['-2'])
        self.assertEqual(['-2'], args.pargs)

    def test_parser_routes_following_option_value_to_parseargs(self):
        parser = Parser(None, None, None, None, None)
        method = _FakeMethod()
        parser.get_method = lambda command: method
        parser.methodize(['$yt', '-s', 'foo'])
        self.assertEqual('foo', method._raw_args.get_val('s'))
