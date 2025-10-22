import pickle
from enum import Enum

import msgspec.json

from gdo.base.Application import Application
from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDT_Text import GDT_Text


class SerializeMode(Enum):
    JSON = 1
    PICKLE = 2
    MSGPACK = 3
    GDOPACK = 4


class GDT_Serialize(GDT_Text):
    _mode: SerializeMode

    def __init__(self, name: str):
        super().__init__(name)
        self._mode = SerializeMode.JSON
        # self.binary()
        self.maxlen(65535)

    def mode(self, mode: SerializeMode):
        self._mode = mode
        return self

    def to_val(self, value) -> bytes | str | None:
        if not value:
            return None
        if self._mode == SerializeMode.JSON:
            return msgspec.json.encode(value)
        if self._mode == SerializeMode.MSGPACK:
            return msgspec.msgpack.encode(value)
        if self._mode == SerializeMode.GDOPACK:
            return value.gdopack()
        return pickle.dumps(value)

    def to_value(self, val: bytes | str):
        if val is None:
            return None
        if self._mode == SerializeMode.JSON:
            return msgspec.json.decode(val)
        if self._mode == SerializeMode.MSGPACK:
            return msgspec.msgpack.decode(val)
        if self._mode == SerializeMode.GDOPACK:
            return WithSerialization.gdounpack(val)
        return pickle.loads(val)

    def validate(self, val: str|None) -> bool:
        return super().validate(val) if val is None else True
