import os
import tempfile
import unittest
from pathlib import Path

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.connector.Web import Web
from gdo.mail.Mail import Mail
from gdotest.TestUtil import GDOTestCase, web_plug


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


class MailFormTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        self.target = await Web.get_server().get_or_create_user('mail_form_target')
        self.target.save_setting('email', 'mail-form-target@example.test')

    def test_send_form_uses_one_textarea_for_the_body(self):
        out = web_plug(f'mail.send.to.{self.target.get_id()}.html?_lang=en').user('gizmore').exec()

        self.assertIn('id="body" name="body"', out)
        self.assertNotIn('name="body[]"', out)


if __name__ == '__main__':
    unittest.main()
