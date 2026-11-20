import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

from gdo.base.Backup import Backup
from gdo.base.method.backup_make_now import backup_make_now
from gdo.core.GDO_Permission import GDO_Permission


class BackupMakeNowTest(unittest.IsolatedAsyncioTestCase):
    async def test_archives_active_config_database_and_files_privately(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'files').mkdir()
            (root / 'files' / 'test.txt').write_text('file')
            config = root / 'selected.toml'
            config.write_text('test config')
            method = backup_make_now.__new__(backup_make_now)
            method.reply = MagicMock(side_effect=lambda key, args: args[0])
            settings = {'dir.files': 'files', 'db.host': 'localhost', 'db.port': 3306,
                        'db.name': 'test', 'db.user': 'test', 'db.pass': 'test'}
            with patch('gdo.base.method.backup_make_now.Application.CONFIG_PATH', str(config)), \
                 patch('gdo.base.method.backup_make_now.Application.file_path', side_effect=lambda path: str(root / path)), \
                 patch('gdo.base.method.backup_make_now.Application.config', side_effect=settings.get), \
                 patch.object(Backup, 'dump_database', side_effect=lambda path: path.write_text('dump')):
                output = Path(await method.gdo_execute())
            self.assertEqual(GDO_Permission.OWNER, method.gdo_user_permission())
            self.assertEqual('backup.make_now', method.gdo_trigger())
            self.assertEqual(0o600, output.stat().st_mode & 0o777)
            with ZipFile(output) as archive:
                self.assertEqual(['database.sql', 'files/test.txt', 'protected/config.toml'], sorted(archive.namelist()))
                self.assertEqual(b'test config', archive.read('protected/config.toml'))

    async def test_rejects_unsafe_backup_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'protected/backup/full-private'
            target.mkdir(parents=True)
            target.chmod(0o755)
            with patch('gdo.base.method.backup_make_now.Application.file_path', side_effect=lambda path: str(root / path)), \
                 patch('gdo.base.method.backup_make_now.Application.config', return_value='files'), \
                 patch('gdo.base.method.backup_make_now.Backup') as backup:
                with self.assertRaisesRegex(ValueError, 'private'):
                    await backup_make_now.__new__(backup_make_now).gdo_execute()
            backup.assert_not_called()
