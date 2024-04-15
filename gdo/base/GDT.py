class GDT:
    """
    Base class of every other class.
    @version 8.0.0
    """

    NULL_STRING = 'NULL'
    EMPTY_STRING = ''
    GDT_MAX = 0
    GDT_COUNT = 0

    @classmethod
    def escape(cls, val: str) -> str:
        if val is None:
            return cls.EMPTY_STRING
        return (val.replace('\\', '\\\\').
                replace('"', '\\"').
                replace("'", "\\'"))

    @classmethod
    def quote(cls, val: str) -> str:
        if val is None or val == cls.EMPTY_STRING:
            return cls.NULL_STRING
        return f"'{cls.escape(val)}'"

    def __init__(self):
        self.GDT_COUNT += 1
        self.GDT_MAX = max(self.GDT_COUNT, self.GDT_MAX)

    def gdo_before_create(self, gdo):
        pass

    def gdo_after_create(self, gdo):
        pass

    def gdo_before_update(self, gdo):
        pass

    def gdo_after_update(self, gdo):
        pass

    def gdo_before_delete(self, gdo):
        pass

    def gdo_after_delete(self, gdo):
        pass


    def get_name(self):
        return self.__class__.__name__ + "#" + str(id(self))

    def has_error(self) -> bool:
        return False

    def gdo_column_define(self) -> str:
        return self.EMPTY_STRING

    def is_primary(self):
        return False

    def gdo(self, gdo):
        return self

    def val(self, val: str):
        return self

    def value(self, value):
        return self

    def get_val(self):
        return self.EMPTY_STRING

    def get_value(self):
        return None

    def to_val(self, value) -> str:
        if value is None:
            return self.EMPTY_STRING
        return str(value)

    def to_value(self, val: str):
        return val

    def validate(self, value) -> bool:
        return True

    def validated(self, value):
        if self.validate(value):
            return self
        return None

    def is_positional(self) -> bool:
        return False

    ##########
    # Render #
    ##########
    def render_toml(self) -> str:
        return f"{self.get_name()} = \"{self.get_val()}\"\n"

    def get_initial(self):
        return None
