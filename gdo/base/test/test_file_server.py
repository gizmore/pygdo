import unittest
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.method.file_server import file_server


class FileServerTest(unittest.TestCase):

    DIRS = {
        'files': 'files/',
        'assets': 'assets/',
        'temp': 'temp/',
        'cache': 'temp/cache/',
        'logs': 'protected/logs/',
        'config': 'protected/',
    }

    def setUp(self):
        file_server.is_forbidden.cache_clear()
        self.addCleanup(file_server.is_forbidden.cache_clear)

    @patch('gdo.base.method.file_server.module_config_value', return_value=False)
    @patch.object(Application, 'config', return_value=DIRS)
    def test_forbids_private_and_traversal_paths(self, _config, _module_config):
        for url in (
            'files/gdo_file/1',
            'protected/config.toml',
            'protected/logs/debug.log',
            'temp/cache/session',
            '../protected/config.toml',
            '%2e%2e/protected/config.toml',
            'files\\gdo_file\\1',
        ):
            with self.subTest(url=url):
                self.assertTrue(file_server.is_forbidden(url))


if __name__ == '__main__':
    unittest.main()
