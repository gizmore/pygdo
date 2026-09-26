import os
import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.base.Application import Application
from gdo.mail.GDT_Email import GDT_Email


class EmailEncodingTest(GDOTestCase):
    """Portable account addresses must not silently accept SMTPUTF8 input."""

    @classmethod
    def setUpClass(cls):
        Application.init(os.path.dirname(__file__) + '/../../../')

    def test_rejects_umlaut_in_local_part(self):
        self.assertFalse(GDT_Email('email').validate('mïra@example.test'))

    def test_rejects_umlaut_in_domain(self):
        self.assertFalse(GDT_Email('email').validate('mira@exämple.test'))

    def test_accepts_ascii_address(self):
        self.assertTrue(GDT_Email('email').validate('mira@example.test'))


if __name__ == '__main__':
    unittest.main()
