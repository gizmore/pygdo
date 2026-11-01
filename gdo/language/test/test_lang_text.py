import unittest
from unittest.mock import MagicMock, patch

from gdo.language.GDO_LangText import GDO_LangText


class LangTextTest(unittest.TestCase):
    def test_lookup_uses_fallback_and_preserves_empty_translation(self):
        row = MagicMock()
        row.gdo_val.return_value = ''
        table = MagicMock()
        table.get_by_id.side_effect = [None, row]
        with patch.object(GDO_LangText, 'table', return_value=table):
            self.assertEqual('', GDO_LangText.lookup('category', '1', 'de', 'en'))
        self.assertEqual(2, table.get_by_id.call_count)

    def test_lookup_does_not_query_same_language_twice(self):
        table = MagicMock()
        table.get_by_id.return_value = None
        with patch.object(GDO_LangText, 'table', return_value=table):
            self.assertIsNone(GDO_LangText.lookup('category', '1', 'en', 'en'))
        table.get_by_id.assert_called_once_with('category', '1', 'en')
