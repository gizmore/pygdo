import json
import pickle
from enum import Enum

import msgpack

# from gdo.base.WithMsgpackSupport import WithMsgpackSupport
from gdo.core.GDT_Text import GDT_Text




class Mode(Enum):
    JSON = 1
    PICKLE = 2
    MSGPACK = 3


# class DictSerializableMixin:
#     def to_dict(self):
#         """Convert object to a dictionary, recursively handling nested objects."""
#         return {
#             key: value.to_dict() if isinstance(value, DictSerializableMixin) else value
#             for key, value in self.__dict__.items()
#         }
#
#     @classmethod
#     def from_dict(cls, data):
#         """Create an object from a dictionary, recursively instantiating nested objects."""
#         obj = cls.__new__(cls)  # Create an empty instance without calling __init__
#         for key, value in data.items():
#             setattr(obj, key, value)
#         return obj


# class GDODict(WithMsgpackSupport):
#
#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             if isinstance(value, dict):
#                 value = GDODict(**value)
#             setattr(self, key, value)
#
#     def __getitem__(self, key):
#         return getattr(self, key)
#
#     def __setitem__(self, key, value):
#         setattr(self, key, value)
#
#     def __contains__(self, key):
#         return hasattr(self, key)
#
#     def items(self):
#         return self.__dict__.items()
#
#     def keys(self):
#         return self.__dict__.keys()
#
#     def values(self):
#         return self.__dict__.values()
#
#     def __repr__(self):
#         return f"GDODict({self.__dict__})"


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
        if self._mode == Mode.MSGPACK:
            return msgpack.dumps(value)
        if self._mode == Mode.JSON:
            return json.dumps(value)
        return pickle.dumps(value)

    def to_value(self, val: bytes | str):
        if val is None:
            return None
        if self._mode == Mode.MSGPACK:
            return msgpack.loads(val)
        if self._mode == Mode.JSON:
            return json.loads(val)
        return pickle.loads(val)

    def validate(self, val: str | None, value: any) -> bool:
        if value is None:
            return super().validate(val, value)
        return True
