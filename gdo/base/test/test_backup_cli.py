import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    'gdo_backup_cli', Path(__file__).resolve().parents[3] / 'bin' / 'gdo_backup.py')
backup_cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup_cli)


class BackupCLITest(unittest.TestCase):
    def test_acl_allows_only_mira_and_denies_group_and_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            target.chmod(0o770)
            good = 'user::rwx\nuser:mira:rwx\ngroup::---\nmask::rwx\nother::---\n'
            with patch.object(backup_cli.subprocess, 'run') as run:
                run.return_value.stdout = good
                self.assertTrue(backup_cli.private_backup_directory(target))
                run.return_value.stdout = good.replace('group::---', 'group::r-x')
                self.assertFalse(backup_cli.private_backup_directory(target))
                run.return_value.stdout = good + 'user:someone:r--\n'
                self.assertFalse(backup_cli.private_backup_directory(target))
                run.return_value.stdout = ''
                self.assertFalse(backup_cli.private_backup_directory(target))

    def test_selected_config_is_used_without_archiving_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / 'protected').mkdir()
            (project / 'uploads').mkdir()
            config = project / 'other.toml'
            config.write_text('[db]\nhost="db"\nport=3306\nname="test"\nuser="u"\npass="p"\n'
                              '[dir]\nfiles="uploads"\n', encoding='utf-8')
            with patch.object(backup_cli, 'PROJECT', project), \
                    patch.object(backup_cli, 'Backup') as backup, \
                    patch('sys.argv', ['gdo_backup.py', '--config=other.toml']):
                self.assertEqual(0, backup_cli.main())
            self.assertEqual('test', backup.call_args.args[2]['name'])
            self.assertEqual(project / 'uploads', backup.call_args.args[1])
            backup.return_value.archive.assert_called_once_with(
                project / 'protected' / 'backup', include_config=False)
            self.assertEqual(0o700, (project / 'protected' / 'backup').stat().st_mode & 0o777)

    def test_missing_config_fails(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(backup_cli, 'PROJECT', Path(tmp)), \
                patch('sys.argv', ['gdo_backup.py']):
            self.assertEqual(1, backup_cli.main())

    def test_quick_dump_does_not_require_files_or_create_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / 'protected').mkdir()
            (project / 'protected' / 'config.toml').write_text(
                '[db]\nhost="db"\nport=3306\nname="test"\nuser="u"\npass="p"\n', encoding='utf-8')
            def dump(path):
                path.write_text('SELECT 1;', encoding='utf-8')
            with patch.object(backup_cli, 'PROJECT', project), \
                    patch.object(backup_cli.socket, 'gethostname', return_value='mogwai'), \
                    patch.object(backup_cli.Backup, 'dump_database', side_effect=dump), \
                    patch('sys.argv', ['gdo_backup.py', '--quick']):
                self.assertEqual(0, backup_cli.main())
                self.assertEqual(0, backup_cli.main())
            outputs = list((project / 'protected' / 'backup').iterdir())
            self.assertEqual(2, len(outputs))
            self.assertTrue(all(p.suffix == '.sql' and 'mogwai' in p.name for p in outputs))
            self.assertTrue(all(p.read_text() == 'SELECT 1;' for p in outputs))
            self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in outputs))

    def test_quick_dump_failure_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with patch.object(backup_cli.Backup, 'dump_database', side_effect=OSError):
                with self.assertRaises(OSError):
                    backup_cli.quick_backup(backup_cli.Backup('c', target, {}), target)
            self.assertEqual([], list(target.iterdir()))
