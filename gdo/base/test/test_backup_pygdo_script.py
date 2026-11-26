import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[4]


@unittest.skipUnless((WORKSPACE / 'gdo_backup_pygdo.py').is_file(), 'backup helper unavailable')
class PyGDOBackupScriptTest(unittest.TestCase):
    def git(self, directory, *args):
        subprocess.run(['git', '-C', str(directory), *args], check=True, capture_output=True)

    def test_repository_selection_and_ignored_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('gdo_backup_pygdo.sh', 'gdo_backup_pygdo.py'):
                shutil.copyfile(WORKSPACE / name, root / name)
            project = root / 'pygdo'
            project.mkdir()
            self.git(project, 'init', '-q')
            (project / '.gitignore').write_text('/gdo/*\n/protected/\n/files/\n')
            (project / 'source.py').write_text('tracked')
            (project / 'untracked.py').write_text('not ignored')
            self.git(project, 'add', '.gitignore', 'source.py')
            self.git(project, 'update-index', '--add', '--cacheinfo',
                     '160000,1111111111111111111111111111111111111111,vendor')
            (project / 'vendor').mkdir()
            (project / 'vendor' / 'secret').write_text('submodule')
            for rel in ('protected/secret', 'files/git_repo/private', 'files/other'):
                path = project / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('ignored')
            for name, origin in (('own', 'https://github.com/mira-gpt/pygdo-own'),
                                 ('thirdparty', 'https://github.com/other/thirdparty')):
                repo = project / 'gdo' / name
                repo.mkdir(parents=True)
                self.git(repo, 'init', '-q')
                self.git(repo, 'remote', 'add', 'origin', origin)
                (repo / '.gitignore').write_text('ignored.txt\n')
                (repo / 'tracked.py').write_text('tracked')
                (repo / 'ignored.txt').write_text('ignored')
                (repo / 'untracked.py').write_text('not ignored')
                self.git(repo, 'add', '.gitignore', 'tracked.py')
                self.git(repo, 'update-index', '--add', '--cacheinfo',
                         '160000,1111111111111111111111111111111111111111,vendor')
                (repo / 'vendor').mkdir()
                (repo / 'vendor' / 'secret').write_text('submodule')
            destination = root / 'backups'
            destination.mkdir()
            subprocess.run(['bash', str(root / 'gdo_backup_pygdo.sh')], check=True, capture_output=True,
                           env={**os.environ, 'PYGDO_BACKUP_DIR': str(destination)})
            archives = list(destination.glob('*_pygdo.zip'))
            self.assertEqual(len(archives), 1)
            self.assertEqual(archives[0].stat().st_mode & 0o077, 0)
            with zipfile.ZipFile(archives[0]) as archive:
                names = set(archive.namelist())
            self.assertTrue({'pygdo/gdo/own/tracked.py', 'pygdo/gdo/own/ignored.txt',
                             'pygdo/gdo/thirdparty/tracked.py', 'pygdo/gdo/thirdparty/ignored.txt'} <= names)
            self.assertNotIn('pygdo/source.py', names)
            self.assertNotIn('pygdo/protected/secret', names)
            self.assertFalse(any('.git/' in name or 'untracked.py' in name
                                 or 'git_repo/' in name or 'vendor/' in name for name in names))

    def test_refuses_destination_inside_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('gdo_backup_pygdo.sh', 'gdo_backup_pygdo.py'):
                shutil.copyfile(WORKSPACE / name, root / name)
            project = root / 'pygdo'
            project.mkdir()
            self.git(project, 'init', '-q')
            destination = project / 'backup'
            destination.mkdir()
            result = subprocess.run(['bash', str(root / 'gdo_backup_pygdo.sh')], capture_output=True,
                                    env={**os.environ, 'PYGDO_BACKUP_DIR': str(destination)})
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(list(destination.iterdir()))
