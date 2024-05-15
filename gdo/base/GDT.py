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
    GDT_MAX = 0
    GDT_COUNT = 0
    GDT_ALIVE = 0

    __slots__ = ()

    @classmethod
    def escape(cls, val: str) -> str:
        if val is None:
            return ''
        return (val.replace('\\', '\\\\').
                replace('"', '\\"').
                replace("'", "\\'"))

    @classmethod
    def quote(cls, val: str) -> str:
        if val is None or val == '':
            return cls.NULL_STRING
        return f"'{cls.escape(val)}'"

    def __init__(self):
        from gdo.base.Application import Application
        if Application.config('core.gdt_debug') == '2':
            from gdo.base.Logger import Logger
            Logger.debug(str(self.__class__) + "".join(traceback.format_stack()))
        GDT.GDT_COUNT += 1
        GDT.GDT_ALIVE += 1
        GDT.GDT_MAX = max(GDT.GDT_ALIVE, GDT.GDT_MAX)

    def __del__(self):
        GDT.GDT_ALIVE -= 1

    #############
    ### Hooks ###
    #############

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

    ##########
    # Errors #
    ##########
    def has_error(self) -> bool:
        return False

    def render_error(self) -> str:
        return ''

    def error(self, key: str, args: list[str] = None) -> bool:
        return False

    def reset_error(self):
        return self

    def get_name(self):
        return self.__class__.__name__ + "#" + str(id(self))

    def gdo_column_define(self) -> str:
        return ''

    def column_define_fk(self) -> str:
        return ''

    def is_primary(self) -> bool:
        return False

    def is_unique(self) -> bool:
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
        return None

    def is_not_null(self) -> bool:
        return False

    def get_value(self):
        return None

    def to_val(self, value) -> str:
        if value is None:
            return ''
        return str(value)

    def to_value(self, val: str):
        return val

    def validate(self, value) -> bool:
        return True

    def validated(self):
        self.reset_error()
        if self.validate(self.get_value()):
            return self
        return None

    def is_positional(self) -> bool:
        return False

    def has_fields(self) -> bool:
        return False

    def writable(self, writable: bool = True):
        pass

    def is_writable(self) -> bool:
        return False

    def is_hidden(self) -> bool:
        return False

    def has_tooltip(self) -> bool:
        return False

    def fields(self) -> list:
        return []

    def all_fields(self):
        return []

    def is_orderable(self) -> bool:
        return False

    def default_order(self) -> str:
        return 'ASC'

    ###################
    # Render HTML TPL #
    ###################

    def html_value(self):
        return Strings.html(self.get_val())

    def html_class(self):
        return self.__class__.__name__.lower().replace('_', '-')

    def filter_type(self) -> str:
        return 'text'

    ##############
    # Render GDO #
    ##############
    def render(self, mode: Mode = Mode.HTML):
        return self.render_gdt(mode)

    def render_gdt(self, mode: Mode):
        """
        Call the appropriate render method
        """
        method_name = f'render_{mode.name.lower()}'
        method = getattr(self, method_name)
        return method()

    def render_toml(self) -> str:
        return f"{self.get_name()} = \"{self.get_val()}\"\n"

    def render_html(self) -> str:
        return Strings.html(self.get_val())

    def render_telegram(self):
        return self.render_txt()

    def render_form(self) -> str:
        return ''

    def render_cell(self) -> str:
        return self.render_html()

    def render_cli(self) -> str:
        return self.render_txt()

    def render_txt(self) -> str:
        return str(self.get_val())

    def render_irc(self) -> str:
        return self.render_txt()

    def render_val(self) -> str:
        return self.display_val(self.get_val())

    def render_suggestion(self) -> str:
        return ''

    def display_val(self, val: str) -> str:
        return val
