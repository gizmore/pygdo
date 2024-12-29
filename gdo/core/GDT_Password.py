import bcrypt
from gdo.core.GDT_String import GDT_String


class GDT_Password(GDT_String):
    SALT_LEN: int = 12

    def __init__(self, name):
        super().__init__(name)
        self.minlen(4)
        self._input_type = 'password'

    @classmethod
    def check(cls, hash_: str, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode('utf-8'), hash_.encode('utf-8'))

    @classmethod
    def hash(cls, plain: str):
        return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(cls.SALT_LEN)).decode('utf-8')

    def val(self, val: str | list):
        if val is None:
            return self
        return super().val(self.hash(val))
