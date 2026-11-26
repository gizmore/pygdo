import hashlib
import unittest
from unittest.mock import MagicMock

from gdo.base.GDO import GDO


class TestGDOHashBytes(unittest.TestCase):
    def test_hash_accepts_serialized_bytes_and_preserves_text_hashes(self):
        instance = MagicMock()
        fields = []
        for value in ('hello', b'{"key":"value"}', None):
            field = MagicMock()
            field.gdo.return_value.get_val.return_value = value
            fields.append(field)
        instance.columns.return_value = dict(enumerate(fields))
        instance.HASH_LENGTH = GDO.HASH_LENGTH
        expected = hashlib.sha256(b'hello{"key":"value"}').hexdigest()[:GDO.HASH_LENGTH]
        self.assertEqual(expected, GDO.gdo_hash(instance))

