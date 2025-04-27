import unittest

from gdo.mail.Mail import Mail
from gdotest.TestUtil import GDOTestCase


class MailTestCase(GDOTestCase):

    def test_01_lazy_mail(self):
        mail = Mail.from_bot()
        mail.recipient('gizmore@gizmore.org', 'gizmore')
        mail.subject('Test Mail')
        mail.body('<a href="/test.html">test</a>')
        mail.send()
        mail.lazy().send()

    def test_01_html_and_text_mail(self):
        pass


if __name__ == '__main__':
    unittest.main()
