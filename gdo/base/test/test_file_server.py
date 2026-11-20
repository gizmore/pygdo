import unittest
import tempfile
from pathlib import Path
from gdotest.TestUtil import GDOTestCase
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.method.file_server import file_server
from gdo.base.GDT_RawResponse import GDT_RawResponse
from gdo.file.GDT_FileOut import GDT_FileOut


class FileServerTest(GDOTestCase):

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
            'gdo/example/settings.toml',
            'gdo/example/SETTINGS.TOML',
            'gdo/example/settings%2Etoml',
            'gdo/example/secret_key',
            'gdo/example/Secret_key',
        ):
            with self.subTest(url=url):
                self.assertTrue(file_server.is_forbidden(url))

    @patch('gdo.base.method.file_server.module_config_value', return_value=False)
    @patch.object(Application, 'config', return_value=DIRS)
    def test_allows_non_sensitive_file(self, _config, _module_config):
        self.assertFalse(file_server.is_forbidden('gdo/example/image.png'))

    def test_markdown_preview_is_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'README.md'
            path.write_text('# Hello\n\n**World**', encoding='utf-8')
            method = file_server.__new__(file_server)
            with patch.object(method, 'get_seo_file', return_value=None), \
                 patch.object(method, 'get_url', return_value='README.md'), \
                 patch.object(method, 'get_path', return_value=str(path)), \
                 patch.object(method, 'param_val', return_value='1'), \
                 patch.object(file_server, 'is_forbidden', return_value=False), \
                 patch('gdo.base.method.file_server.module_enabled', return_value=True), \
                 patch.object(Application, 'header'):
                result = method.gdo_execute()
            self.assertIsInstance(result, GDT_RawResponse)
            self.assertIn(b'<h1>Hello</h1>', result.body)
            self.assertIn(b'<strong>World</strong>', result.body)
            self.assertIn(b'<style>', result.body)
            self.assertIn(b'prefers-color-scheme: dark', result.body)

            with patch.object(method, 'get_seo_file', return_value=None), \
                 patch.object(method, 'get_url', return_value='README.md'), \
                 patch.object(method, 'get_path', return_value=str(path)), \
                 patch.object(method, 'param_val', return_value='1'), \
                 patch.object(file_server, 'is_forbidden', return_value=False), \
                 patch.object(file_server, 'check_etag', return_value=False), \
                 patch('gdo.base.method.file_server.module_enabled', return_value=False), \
                 patch.object(Application, 'header'):
                self.assertIsInstance(method.gdo_execute(), GDT_FileOut)


if __name__ == '__main__':
    unittest.main()
