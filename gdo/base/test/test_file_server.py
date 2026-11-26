import unittest
import tempfile
from pathlib import Path
from gdotest.TestUtil import GDOTestCase
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.method.file_server import MarkdownMetadata, file_server
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

    def test_markdown_metadata_uses_first_elements_and_ignores_scripts(self):
        metadata = MarkdownMetadata()
        metadata.feed('<script><h1>ignored</h1></script><h2>First <em>heading</em></h2>'
                      '<h1>Second</h1><p>First <a href="#">paragraph</a>.</p><p>Second.</p>')
        self.assertEqual('First heading', metadata.title)
        self.assertEqual('First paragraph.', metadata.description)

    def test_markdown_metadata_handles_missing_fields(self):
        metadata = MarkdownMetadata()
        metadata.feed('<pre>Only code</pre>')
        self.assertIsNone(metadata.title)
        self.assertIsNone(metadata.description)

    def test_public_markdown_uses_link_preview_api(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'README.md'
            source.write_text('# A title\n\nA paragraph.', encoding='utf-8')
            method = file_server.__new__(file_server)
            with patch.object(method, 'get_seo_file', return_value=None), \
                    patch.object(method, 'get_url', return_value='README.md'), \
                    patch.object(method, 'get_path', return_value=str(source)), \
                    patch.object(method, 'param_val', return_value='1'), \
                    patch.object(file_server, 'is_forbidden', return_value=False), \
                    patch.object(Application, 'file_path', return_value=directory), \
                    patch('gdo.base.method.file_server.module_enabled', return_value=True), \
                    patch.object(Application, 'header'), \
                    patch('gdo.link_preview.MarkdownPreview.MarkdownPreview.for_html',
                          return_value='https://example.test/image.png') as preview:
                result = method.gdo_execute()
            self.assertIn(b'<meta property="og:image" content="https://example.test/image.png">', result.body)
            preview.assert_called_once()

    def test_token_routed_markdown_does_not_generate_public_image(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'README.md'
            source.write_text('# Private\n\nSecret text.', encoding='utf-8')
            method = file_server.__new__(file_server)
            method._explicitly_allowed = True
            with patch.object(method, 'get_seo_file', return_value=object()), \
                    patch.object(method, 'get_url', return_value='README.md'), \
                    patch.object(method, 'get_path', return_value=str(source)), \
                    patch.object(method, 'param_val', return_value='1'), \
                    patch.object(Application, 'file_path', return_value=directory), \
                    patch('gdo.base.method.file_server.module_enabled', return_value=True), \
                    patch.object(Application, 'header'), \
                    patch('gdo.link_preview.MarkdownPreview.MarkdownPreview.for_html') as preview:
                result = method.gdo_execute()
            self.assertNotIn(b'og:image', result.body)
            preview.assert_not_called()

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
            'gdo/example/%73ecret/image.png',
        ):
            with self.subTest(url=url):
                self.assertTrue(file_server.is_forbidden(url))

    @patch('gdo.base.method.file_server.module_config_value', return_value=False)
    @patch.object(Application, 'config', return_value=DIRS)
    def test_allows_non_sensitive_file(self, _config, _module_config):
        self.assertFalse(file_server.is_forbidden('gdo/example/image.png'))

    def test_secret_path_cannot_bypass_through_explicit_or_seo_route(self):
        method = file_server.__new__(file_server)
        method._explicitly_allowed = True
        with patch.object(method, 'get_url', return_value='public/%73ecret/image.png'), \
             patch.object(method, 'get_seo_file') as seo, \
             patch.object(method, 'err', return_value='forbidden'), \
             patch.object(Application, 'status') as status:
            self.assertEqual('forbidden', method.gdo_execute())
        status.assert_called_once_with('403 Forbidden')
        seo.assert_not_called()

    def test_markdown_preview_is_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'README.md'
            path.write_text('# Hello *there* & friends\n\n**World** "test" & more', encoding='utf-8')
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
            self.assertIn(b'<h1>Hello <em>there</em> &amp; friends</h1>', result.body)
            self.assertIn(b'<strong>World</strong>', result.body)
            self.assertIn(b'<title>Hello there &amp; friends</title>', result.body)
            self.assertIn(b'<meta name="description" content="World &quot;test&quot; &amp; more">', result.body)
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
