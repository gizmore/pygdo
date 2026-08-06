import tempfile
import unittest
from pathlib import Path

from gdo.mail.Mail import Mail


class MailAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name) / 'log.txt'
        self.file.write_bytes(b'log attachment\n')
        self.mail = (Mail()
                     .sender('dog@example.test', 'Dog')
                     .recipient('gizmore@example.test')
                     .subject('Log archive')
                     .body('Attached log.'))
        self.mail._body_html = lambda: '<p>Attached log.</p>'
        self.mail._body_text = lambda: 'Attached log.'

    def tearDown(self):
        self.temp.cleanup()

    def test_attachment_is_included_in_mime_message(self):
        self.mail.attachment(self.file)

        message = self.mail.build_message()
        attachment = message.get_payload()[-1]
        self.assertEqual('attachment; filename="log.txt"', attachment['Content-Disposition'])
        self.assertEqual(b'log attachment\n', attachment.get_payload(decode=True))

    def test_attachment_name_can_be_overridden(self):
        self.mail.attachment(self.file, 'logs-2026.zip')

        attachment = self.mail.build_message().get_payload()[-1]
        self.assertEqual('attachment; filename="logs-2026.zip"', attachment['Content-Disposition'])

    def test_attachment_rejects_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.mail.attachment(Path(self.temp.name) / 'missing.log')


if __name__ == '__main__':
    unittest.main()
