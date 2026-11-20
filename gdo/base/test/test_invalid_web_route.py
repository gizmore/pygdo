import unittest
from unittest.mock import patch

from gdo.base.Exceptions import GDOModuleException
from gdo.base.ParseArgs import ParseArgs


class InvalidWebRouteTest(unittest.TestCase):
    def test_malformed_paths_are_expected_not_found_without_exception_logging(self):
        for path in ('/resend-config.json', '/foo', '/.method.html', '/module..html', '/module.method.'):
            with self.subTest(path=path), patch('gdo.base.ParseArgs.Logger.exception') as log:
                with self.assertRaises(GDOModuleException):
                    ParseArgs().add_path_vars(path)
                log.assert_not_called()

    def test_valid_route_still_parses(self):
        args = ParseArgs()
        args.add_path_vars('/core.test.value.html')
        self.assertEqual((args.module, args.method, args.mode), ('core', 'test', 'html'))
        self.assertEqual(args._web_path_values, ['value'])
