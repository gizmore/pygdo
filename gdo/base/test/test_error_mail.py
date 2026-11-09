import unittest
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.ErrorMail import report_exception


class ErrorMailTest(unittest.TestCase):
    def config(self, **overrides):
        values = {'mail.errors_to': 'errors@example.test', 'mail.sender': 'mira@example.test',
                  'mail.debug': '0', 'mail.host': 'localhost', 'mail.port': '587',
                  'mail.tls': '1', 'mail.user': 'login', 'mail.pass': 'secret'}
        values.update(overrides)
        return lambda key, default='': values.get(key, default)

    def test_empty_recipient_never_connects(self):
        for value in ('', '   ', None):
            with self.subTest(value=value), \
                    patch.object(Application, 'config', side_effect=self.config(**{'mail.errors_to': value})), \
                    patch('gdo.base.ErrorMail.smtplib.SMTP') as smtp:
                self.assertFalse(report_exception(ValueError('secret')))
                smtp.assert_not_called()

    def test_send_includes_stack_without_sensitive_message_or_locals(self):
        try:
            raise ValueError('password=secret')
        except ValueError as error:
            with patch.object(Application, 'config', side_effect=self.config()), \
                    patch('gdo.base.ErrorMail.smtplib.SMTP') as smtp:
                self.assertTrue(report_exception(error))
        client = smtp.return_value.__enter__.return_value
        message = client.send_message.call_args.args[0]
        self.assertIn('ValueError', message['Subject'])
        body = message.get_body(preferencelist=('plain',)).get_content()
        self.assertIn('test_error_mail.py', body)
        self.assertIn('test_send_includes_stack', body)
        self.assertNotIn('secret', body)
        client.starttls.assert_called_once()

    def test_debug_and_header_injection_do_not_send(self):
        for values in ({'mail.debug': '1'}, {'mail.errors_to': 'x@example.test\nBcc: evil@example.test'}):
            with self.subTest(values=values), patch.object(Application, 'config', side_effect=self.config(**values)), \
                    patch('gdo.base.ErrorMail.smtplib.SMTP') as smtp:
                self.assertFalse(report_exception(ValueError('x')))
                smtp.assert_not_called()

    def test_mail_failure_does_not_propagate(self):
        with patch.object(Application, 'config', side_effect=self.config()), \
                patch('gdo.base.ErrorMail.smtplib.SMTP', side_effect=OSError('secret')), \
                patch('gdo.base.ErrorMail.sys.stderr') as stderr:
            self.assertFalse(report_exception(ValueError('x')))
        self.assertNotIn('secret', str(stderr.write.call_args))

    def test_logger_invokes_error_notification(self):
        from gdo.base.Logger import Logger
        error = ValueError('example')
        with patch.object(Logger, 'traceback', return_value='stack'), \
                patch.object(Logger, 'write'), patch('gdo.base.Logger.sys.stderr'), \
                patch('gdo.base.ErrorMail.report_exception') as report:
            Logger.exception(error)
        report.assert_called_once_with(error)

    def test_new_install_default_recipient_is_empty(self):
        from gdo.install.Config import Config
        fields = Config.defaults()
        self.assertIn(fields['mail.errors_to'], ('', None))
