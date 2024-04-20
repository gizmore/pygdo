import unittest

from gdo.mail.Mail import Mail


class MailTestCase(unittest.TestCase):

    def test_01_lazy_mail(self):
        mail = Mail.from_bot()
        mail.recipient('gizmore@gizmore.org', 'gizmore')
        mail.subject('Test Mail')
        mail.body('<a href="/test.html">')
        mail.send()
        mail.lazy().send()
        pass

    def test_01_html_and_text_mail(self):
        pass


if __name__ == '__main__':
    unittest.main()
