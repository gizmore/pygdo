import base64

from gdo.core.GDT_String import GDT_String


class GDT_Base64(GDT_String):

    @classmethod
    def encode(cls, s: str) -> str:
        return base64.b64encode(s.encode()).decode()

    @classmethod
    def decode(cls, s: str) -> str:
        return base64.b64decode(s.encode()).decode()

    def to_value(self, val: str):
        return self.decode(val)

    def to_val(self, value) -> str:
        return self.encode(value)
