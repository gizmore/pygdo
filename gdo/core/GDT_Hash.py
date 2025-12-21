import hashlib

from gdo.core.GDT_Char import GDT_Char


class GDT_Hash(GDT_Char):

    _type: str

    TYPES = {
        'sha256': 256 // 4,
        'md5': 128 // 4,
    }

    def __init__(self, name: str):
        super().__init__(name)
        self.type('sha256')
        self.ascii()
        self.case_i()

    def type(self, type: str):
        self._type = type
        return self.maxlen(self.TYPES.get(type))

    def hash(self, s: str):
        return self.to_val(s)

    def to_val(self, value) -> str:
        return getattr(hashlib, self._type)(value.encode()).hexdigest()
