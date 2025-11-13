from gdo.core.GDT_String import GDT_String


class GDT_Password(GDT_String):
    SALT_LEN: int = 12
    BCRYPT = None

    def __init__(self, name):
        super().__init__(name)
        self.minlen(4)
        self._input_type = 'password'
        self.icon('password')

    @classmethod
    def check(cls, hash_: str, plain: str) -> bool:
        return cls.bcrypt().checkpw(plain.encode(), hash_.encode())

    @classmethod
    def hash(cls, plain: str):
        return cls.bcrypt().hashpw(plain.encode(), cls.bcrypt().gensalt(cls.SALT_LEN)).decode()

    @classmethod
    def bcrypt(cls):
        if not cls.BCRYPT:
            import bcrypt
            cls.BCRYPT = bcrypt
        return cls.BCRYPT

    def val(self, val: str | list):
        val = val[0] if type(val) is list else val
        if not val or val[0] == '$':
            return super().val(val)
        else:
            return super().val(self.hash(val))
