import json
import pickle
from enum import Enum

import msgpack

from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDT_Text import GDT_Text


class Mode(Enum):
    JSON = 1
    PICKLE = 2
    MSGPACK = 3
    GDOPACK = 4


class GDT_Serialize(GDT_Text):
    _mode: Mode

    def __init__(self, name: str):
        super().__init__(name)
        self._mode = Mode.JSON
        self.binary()
        self.maxlen(65535)

    def mode(self, mode: Mode):
        self._mode = mode
        return self

    def to_val(self, value) -> bytes | str | None:
        if not value:
            return None
        if self._mode == Mode.GDOPACK:
            return value.gdopack()
        if self._mode == Mode.MSGPACK:
            return msgpack.dumps(value)
        if self._mode == Mode.JSON:
            return json.dumps(value)
        return pickle.dumps(value)

    def to_value(self, val: bytes | str):
        if val is None:
            return None
        if self._mode == Mode.GDOPACK:
            return WithSerialization.gdounpack(val)
        if self._mode == Mode.MSGPACK:
            return msgpack.loads(val)
        if self._mode == Mode.JSON:
            return json.loads(val)
        return pickle.loads(val)

    def validate(self, val: str|None) -> bool:
        if val is None:
            return super().validate(val)
        return True
