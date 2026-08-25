import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from gdo.base.Backup import Backup


class BackupTest(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.files = root / 'uploaded-files'
        self.config = root / 'protected' / 'config.toml'
        self.destination = root / 'backups'
        self.config.parent.mkdir()
        self.files.mkdir()
        self.config.write_text('core.secret = "test"', encoding='utf-8')
        (self.files / 'photo.txt').write_text('upload', encoding='utf-8')
        self.backup = Backup(self.config, self.files, {
            'host': 'localhost', 'port': '3306', 'name': 'pygdo',
            'user': 'pygdo', 'pass': 'test',
        })

    def tearDown(self):
        self.temp.cleanup()

    @patch.object(Backup, 'dump_database')
    def test_archives_database_config_and_files_only(self, dump_database):
        dump_database.side_effect = lambda path: path.write_text('CREATE DATABASE pygdo;', encoding='utf-8')
        archive = self.backup.archive(
            self.destination, datetime(2026, 8, 25, 12, 30, 0))
        self.assertEqual('pygdo-data-20260825T123000.zip', archive.name)
        with ZipFile(archive) as zipped:
            self.assertEqual([
                'database.sql',
                'files/photo.txt',
                'protected/config.toml',
            ], sorted(zipped.namelist()))

    @patch.object(Backup, 'dump_database')
    def test_repeated_archives_do_not_overwrite(self, dump_database):
        dump_database.side_effect = lambda path: path.write_text('dump', encoding='utf-8')
        first = self.backup.archive(self.destination, datetime(2026, 8, 25, 12, 30, 0))
        second = self.backup.archive(self.destination, datetime(2026, 8, 25, 12, 30, 0))
        self.assertNotEqual(first, second)

    @patch('gdo.base.Backup.Mail.from_bot')
    def test_mails_archive_as_attachment(self, from_bot):
        archive = self.destination / 'pygdo-data.zip'
        self.destination.mkdir()
        archive.write_text('archive', encoding='utf-8')
        mail = from_bot.return_value
        mail.recipient.return_value = mail
        mail.subject.return_value = mail
        mail.body.return_value = mail
        mail.attachment.return_value = mail
        Backup.mail(archive, 'backup@example.test')
        mail.recipient.assert_called_once_with('backup@example.test')
        mail.attachment.assert_called_once_with(archive)
        mail.send.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
