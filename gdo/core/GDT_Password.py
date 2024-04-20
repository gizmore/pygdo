import bcrypt
from gdo.core.GDT_String import GDT_String


class Password:

    def __init__(self, *, plain: str = None, hashed: str = None):
        self._plain = plain
        self._hash = hashed

    @classmethod
    def hash(cls, plain: str):
        return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')


class GDT_Password(GDT_String):

    @classmethod
    def check(cls, hash_: str, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode('utf-8'), hash_.encode('utf-8'))
