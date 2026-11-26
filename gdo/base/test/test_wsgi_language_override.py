import unittest
from contextvars import copy_context
from unittest.mock import MagicMock, patch

import index_wsgi
from gdo.base.Application import Application
from gdo.base.Trans import Trans


class WSGILanguageOverrideTest(unittest.TestCase):
    def test_valid_language_is_request_local_and_survives_user_reset(self):
        def set_user(_user):
            Application.set_lang_iso('en')

        def request():
            index_wsgi.set_request_user(MagicMock(), 'de')
            self.assertEqual('de', Application.get_lang_iso())
            index_wsgi.set_request_user(MagicMock(), 'de')
            self.assertEqual('de', Application.get_lang_iso())

        with patch.object(Trans, 'CACHE', {'en': {}, 'de': {}}), \
             patch.object(Application, 'set_current_user', side_effect=set_user):
            Application.set_lang_iso('en')
            copy_context().run(request)
            self.assertEqual('en', Application.get_lang_iso())
            index_wsgi.set_request_user(MagicMock(), 'invalid')
            self.assertEqual('en', Application.get_lang_iso())
