
class GDT:

    def has_error(self) -> bool:
        return False

    def gdo_column_define(self) -> str:
        return ""

    def validate(self, value) -> bool:
        return True

    def get_name(self):
        return self.__class__.__name__

    def is_primary(self):
        return False

    @classmethod
    def escape(cls, val: str) -> str:
        return val.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

    @classmethod
    def quote(cls, val: str) -> str:
        if val is None or val == '':
            return 'NULL'
        return f"'{cls.escape(val)}'"

    def gdo(self, gdo):
        return self
