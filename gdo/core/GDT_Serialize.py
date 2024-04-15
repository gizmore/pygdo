import pickle

from gdo.core.GDT_Text import GDT_Text


class GDT_Serialize(GDT_Text):

    def __init__(self, name):
        super().__init__(name)
        self.binary()
        self.maxlen(65535)

    def to_val(self, value) -> bytes:
        return pickle.dumps(value)

    def to_value(self, val: bytes):
        return pickle.loads(val)

    def validate(self, value):
        return True


