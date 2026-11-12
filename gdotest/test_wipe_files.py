import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from gdoadm import App


class TestWipeFiles(unittest.IsolatedAsyncioTestCase):
    async def test_module_wipe_preserves_shared_files(self):
        module = SimpleNamespace(get_name='example', gdo_dependencies=lambda: [])
        loader = MagicMock()
        loader.load_modules_fs.return_value = {'example': module}
        loader.load_modules_db.return_value = [module]
        cache = SimpleNamespace(gdo_execute=AsyncMock())
        with patch('sys.argv', ['gdoadm.py', 'wipe', 'example']), \
                patch('gdoadm.ModuleLoader.instance', return_value=loader), \
                patch('gdoadm.Installer.wipe') as wipe, \
                patch('gdoadm.Files.empty_dir') as empty_dir, \
                patch('gdoadm.clear_cache', return_value=cache):
            await App().wipe()
        wipe.assert_called_once_with(module)
        empty_dir.assert_not_called()
        cache.gdo_execute.assert_awaited_once()

    async def test_full_wipe_clears_shared_files(self):
        db = MagicMock(db_name='test_db')
        cache = SimpleNamespace(gdo_execute=AsyncMock())
        with patch('sys.argv', ['gdoadm.py', 'wipe', '--all']), \
                patch('gdoadm.Application.db', return_value=db), \
                patch('gdoadm.Application.files_path', return_value='/test/files'), \
                patch('gdoadm.Files.empty_dir') as empty_dir, \
                patch('gdoadm.clear_cache', return_value=cache):
            await App().wipe()
        empty_dir.assert_called_once_with('/test/files')
        cache.gdo_execute.assert_awaited_once()
