import unittest

import msgspec

from gdo.base.GDO import GDO
from gdo.base.WithSerialization import WithSerialization


class SerializationTest(unittest.TestCase):
    def test_roundtrip_preserves_blank_state_after_wakeup(self):
        blank = GDO.__new__(GDO)
        blank._blank = True
        restored = WithSerialization.gdounpack(blank.gdopack())
        self.assertTrue(restored._blank)

    def test_old_payload_defaults_to_persisted(self):
        gdo = GDO.__new__(GDO)
        payload = gdo.gdopack2()
        payload.pop('_blank')
        restored = WithSerialization.gdounpack(WithSerialization.MAGIC_NUM + msgspec.msgpack.encode(payload))
        self.assertFalse(restored._blank)
