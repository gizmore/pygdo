import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.method.dir_server import dir_server


class DirectoryServerTest(unittest.TestCase):
    def test_file_links_are_nofollow_but_directories_are_not(self):
        method = dir_server.__new__(dir_server)
        field = MagicMock()
        field.get_val.return_value = 'entry'
        link = MagicMock()
        link.href.return_value = link
        link.text_raw.return_value = link
        with patch.object(dir_server, 'get_path', return_value='public'), \
             patch.object(dir_server, 'get_dir', return_value='/public'), \
             patch('gdo.base.method.dir_server.GDT_Link', return_value=link), \
             patch('gdo.base.method.dir_server.Files.is_dir', return_value=False):
            method.render_file_name(field, None)
            link.nofollow.assert_called_once_with()
        link.reset_mock()
        with patch.object(dir_server, 'get_path', return_value='public'), \
             patch.object(dir_server, 'get_dir', return_value='/public'), \
             patch('gdo.base.method.dir_server.GDT_Link', return_value=link), \
             patch('gdo.base.method.dir_server.Files.is_dir', return_value=True):
            method.render_file_name(field, None)
            link.nofollow.assert_not_called()

    def test_forbidden_request_returns_403_before_listing(self):
        method = dir_server.__new__(dir_server)
        with patch.object(dir_server, 'param_val', return_value='protected/logs'), \
             patch.object(dir_server, 'is_forbidden', return_value=True), \
             patch.object(dir_server, 'err', return_value=MagicMock()) as error, \
             patch.object(Application, 'status') as status:
            method.gdo_execute()
            status.assert_called_once_with('403 Forbidden')
            error.assert_called_once_with('err_file_forbidden')

    def test_markdown_files_get_an_optional_preview_link(self):
        method = dir_server.__new__(dir_server)
        field = MagicMock()
        file = MagicMock()
        file.get_name.return_value = 'My notes.md'
        links = []

        def make_link():
            link = MagicMock()
            link.href.return_value = link
            link.text_raw.return_value = link
            link.icon.return_value = link
            link.attr.return_value = link
            link.nofollow.return_value = link
            link.render.return_value = '<a>link</a>'
            links.append(link)
            return link

        with patch.object(dir_server, 'get_path', return_value='public'), \
             patch.object(dir_server, 'get_dir', return_value='/public'), \
             patch('gdo.base.method.dir_server.GDT_Link', side_effect=make_link), \
             patch('gdo.base.method.dir_server.Files.is_dir', return_value=False), \
             patch('gdo.base.method.dir_server.module_enabled', return_value=True), \
             patch('gdo.base.method.dir_server.t', return_value='View'):
            rendered = method.render_file_preview(field, file)
        links[0].href.assert_called_once_with('/public/My%20notes.md?render_md=1')
        links[0].icon.assert_called_once_with('eye', 'dir_markdown_preview')
        links[0].text_raw.assert_called_once_with('')
        self.assertEqual('<a>link</a>', rendered)

    def test_public_and_private_boundaries(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ('temp', 'protected', 'public'):
                os.mkdir(os.path.join(root, name))
            os.symlink(os.path.join(root, 'protected'), os.path.join(root, 'public', 'link'))
            os.symlink('/etc', os.path.join(root, 'public', 'outside'))
            with patch.object(Application, 'file_path', return_value=root):
                self.assertFalse(dir_server.gdo_needs_authentication(None))
                for path in ('', 'public', 'temperature', 'protectedness'):
                    self.assertFalse(dir_server.is_forbidden(path), path)
                for path in ('temp', 'temp/cache', 'protected', 'protected/logs',
                             'public/../protected', '%2e%2e/protected',
                             'public\\..\\protected', 'public/link', 'public/outside'):
                    self.assertTrue(dir_server.is_forbidden(path), path)


if __name__ == '__main__':
    unittest.main()
