import json
import pickle
from enum import Enum

from gdo.core.GDT_Text import GDT_Text


class Mode(Enum):
    JSON = 1
    PICKLE = 2


class GDT_Serialize(GDT_Text):
    _mode: Mode

    def __init__(self, name):
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
        if self._mode == Mode.JSON:
            return json.dumps(value)
        return pickle.dumps(value)

    def to_value(self, val: bytes | str):
        if val is None:
            return None
        if self._mode == Mode.JSON:
            return json.loads(val)
        return pickle.loads(val)

    def validate(self, val: str | None, value: any) -> bool:
        if value is None:
            return super().validate(val, value)
        return True
