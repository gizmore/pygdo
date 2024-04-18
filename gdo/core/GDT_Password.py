import bcrypt
from gdo.core.GDT_String import GDT_String


class Password:

    def __init__(self, *, plain: str = None, hashed: str = None):
        self._plain = plain
        self._hash = hashed

    @classmethod
    def hash(cls, plain: str):
        return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

    def check(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode('utf-8'), self._hash.encode('utf-8'))


class GDT_Password(GDT_String):
    pass
    # def to_val(self, value) -> str:
    #     if isinstance(value, Password):
    #         return value._hash
    #     else:
    #         return value
    #
    # def to_value(self, val: str):
    #     return Password(plain=val)
    #
