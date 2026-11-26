import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[4] / 'gdo_backup_pygdo.sh'


@unittest.skipUnless(SCRIPT.is_file(), 'workspace backup script is not present')
class PyGDOBackupScriptTest(unittest.TestCase):
    def test_ignored_and_module_files_are_archived(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / SCRIPT.name
            shutil.copyfile(SCRIPT, script)
            for name in ('pygdo/protected/secret.toml', 'pygdo/gdo/example/.gitignore',
                         'pygdo/gdo/example/ignored.txt', 'pygdo/gdo/codegeex/local.py',
                         'pygdo/files/git_repo/project/config', 'pygdo/files/other/git_keep/data',
                         'pygdo/files/git_notes.txt'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('example', encoding='utf8')
            (root / 'pygdo' / 'external-link').symlink_to('/outside/private')
            destination = root / 'backups'
            destination.mkdir()
            result = subprocess.run(['bash', str(script)], check=True, capture_output=True,
                                    env={**os.environ, 'PYGDO_BACKUP_DIR': str(destination)})
            self.assertIn(b'Backup created:', result.stdout)
            archives = list(destination.glob('*_pygdo.zip'))
            self.assertEqual(1, len(archives))
            self.assertEqual(0, archives[0].stat().st_mode & 0o077)
            with zipfile.ZipFile(archives[0]) as archive:
                names = set(archive.namelist())
                self.assertIn('pygdo/protected/secret.toml', names)
                self.assertIn('pygdo/gdo/example/ignored.txt', names)
                self.assertIn('pygdo/gdo/codegeex/local.py', names)
                self.assertNotIn('pygdo/files/git_repo/project/config', names)
                self.assertIn('pygdo/files/other/git_keep/data', names)
                self.assertIn('pygdo/files/git_notes.txt', names)
                self.assertEqual(b'/outside/private', archive.read('pygdo/external-link'))

    def test_refuses_destination_inside_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / SCRIPT.name
            shutil.copyfile(SCRIPT, script)
            destination = root / 'pygdo' / 'backup'
            destination.mkdir(parents=True)
            result = subprocess.run(['bash', str(script)], capture_output=True,
                                    env={**os.environ, 'PYGDO_BACKUP_DIR': str(destination)})
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(list(destination.iterdir()))
