import unittest
from unittest.mock import MagicMock, patch

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

    def test_same_exception_is_reported_at_most_once(self):
        error = ValueError('test')
        with patch.object(Application, 'config', side_effect=self.config()), \
                patch('gdo.base.ErrorMail.smtplib.SMTP') as smtp:
            self.assertTrue(report_exception(error))
            self.assertFalse(report_exception(error))
        smtp.assert_called_once()

    def test_exception_chain_retains_types_and_locations_not_messages(self):
        from gdo.base.ErrorMail import safe_stack
        try:
            try:
                raise ValueError('inner secret')
            except ValueError as cause:
                raise RuntimeError('outer secret') from cause
        except RuntimeError as error:
            stack = safe_stack(error)
        self.assertIn('RuntimeError', stack)
        self.assertIn('ValueError', stack)
        self.assertIn('test_error_mail.py', stack)
        self.assertNotIn('secret', stack)

    def test_async_handler_preserves_previous_and_does_not_install_twice(self):
        from gdo.base.ErrorMail import install_async_exception_handler
        loop = MagicMock()
        previous = MagicMock()
        loop.get_exception_handler.return_value = previous
        install_async_exception_handler(loop)
        handler = loop.set_exception_handler.call_args.args[0]
        error = ValueError('test')
        with patch('gdo.base.Logger.Logger.exception') as log:
            handler(loop, {'exception': error})
        log.assert_called_once_with(error, 'Unhandled asyncio task exception')
        previous.assert_called_once_with(loop, {'exception': error})
        loop.reset_mock()
        loop.get_exception_handler.return_value = handler
        install_async_exception_handler(loop)
        loop.set_exception_handler.assert_not_called()

    def test_new_install_default_recipient_is_empty(self):
        from gdo.install.Config import Config
        fields = Config.defaults()
        self.assertIn(fields['mail.errors_to'], ('', None))
