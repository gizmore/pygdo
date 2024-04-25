import sys
import traceback

from gdo.base.Render import Mode
from gdo.base.Util import Strings, dump


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
        from gdo.base.Application import Application
        if Application.config('core.gdt_debug') == '2':
            from gdo.base.Logger import Logger
            Logger.debug(str(self.__class__) + "".join(traceback.format_stack()))
        GDT.GDT_COUNT += 1
        GDT.GDT_MAX = max(GDT.GDT_COUNT, GDT.GDT_MAX)

    def __del__(self):
        GDT.GDT_COUNT -= 1

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

    def get_initial(self):
        return None

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

    def validated(self):
        if self.validate(self.get_value()):
            return self
        return None

    def is_positional(self) -> bool:
        return False

    def has_fields(self) -> bool:
        return False

    def is_writable(self) -> bool:
        return False

    def is_hidden(self) -> bool:
        return False

    def error(self, key: str, args: list[str] = None) -> bool:
        return False

    ##########
    # Render #
    ##########
    def render(self, mode: Mode = Mode.HTML):
        """
        Call the appropriate render method
        """
        method_name = f'render_{mode.name.lower()}'
        method = getattr(self, method_name)
        return method()

    def html_class(self):
        return self.__class__.__name__.lower().replace('_', '-')

    def render_toml(self) -> str:
        return f"{self.get_name()} = \"{self.get_val()}\"\n"

    def render_html(self) -> str:
        return Strings.html(self.get_val())

    def render_form(self) -> str:
        return ''

    def render_cli(self) -> str:
        return self.get_val()

    def fields(self) -> list:
        return []

