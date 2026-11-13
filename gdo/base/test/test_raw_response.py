import json
import unittest
from unittest.mock import patch

from gdo.base.GDT_RawResponse import GDT_RawResponse
from gdo.core.GDT_Dict import GDT_Dict
from gdo.ui.GDT_Page import GDT_Page


class RawResponseTest(unittest.TestCase):
    def test_raw_json_sets_byte_length_content_type_and_status(self):
        response = GDT_RawResponse.json({'name': 'Ente 🦆'}, 'application/manifest+json', '201 Created')
        with patch('gdo.base.GDT_RawResponse.Application.status') as status, \
             patch('gdo.base.GDT_RawResponse.Application.header') as header:
            body = response.prepare()
        self.assertEqual({'name': 'Ente 🦆'}, json.loads(body))
        status.assert_called_once_with('201 Created')
        header.assert_any_call('Content-Type', 'application/manifest+json')
        header.assert_any_call('Content-Length', str(len(body)))

    def test_normal_json_remains_wrapped(self):
        with patch('gdo.ui.GDT_Page.Application.get_status_code', return_value=200):
            result = GDT_Page().result(GDT_Dict({'answer': 42})).render_json()
        self.assertEqual({'code': 200, 'data': {'answer': 42}}, json.loads(result))
