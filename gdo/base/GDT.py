import binascii
import functools
import traceback
from copy import deepcopy
from typing import Self

from typing_extensions import TYPE_CHECKING

from gdo.base.Trans import Trans, t
from gdo.base.WithSerialization import WithSerialization

if TYPE_CHECKING:
    from gdo.base.Query import Query
    from gdo.base.Method import Method
    from gdo.base.GDO_Module import GDO_Module
    from gdo.form.GDT_Form import GDT_Form

from gdo.base.Render import Mode
from gdo.base.Util import Strings


class GDT(WithSerialization):
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
    def escape(cls, val: str | bytes) -> str:
        if val is None:
            return ''
        if isinstance(val, bytes):
            return binascii.hexlify(val).decode('ascii')
        return (val.replace('\\', '\\\\').
                replace('"', '\\"').
                replace("'", "\\'"))

    @classmethod
    def quote(cls, val: str | bytes) -> str:
        if val is None or val == '':
            return cls.NULL_STRING
        if isinstance(val, bytes):
            return f"UNHEX('{cls.escape(val)}')"
        return f"'{cls.escape(val)}'"

    #PYPP#START#
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
    #PYPP#END#

    def __str__(self):
        return f"{self.get_name()}#{id(self)}"

    def __repr__(self):
        return f"{self.get_name()}#{id(self)}"

    @classmethod
    @functools.cache
    def gdo_module(cls) -> 'GDO_Module':
        from gdo.base.ModuleLoader import ModuleLoader
        mn = cls.__module__
        mn = Strings.substr_from(mn, 'gdo.')
        mn = Strings.substr_to(mn, '.')
        return ModuleLoader.instance()._cache[mn]

    #############
    ### Hooks ###
    #############
    def gdo_file_upload(self, method: 'Method'):
        pass

    def gdo_added_to_form(self, form: 'GDT_Form'):
        pass

    def gdo_before_select(self, gdo, query: 'Query'):
        pass

    def gdo_after_select(self, gdo, query: 'Query'):
        pass

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

    def gdo_form_validated(self, form):
        pass

    def gdo_components(self) -> list['GDT']:
        return []

    def gdo_compare(self, gdt: 'GDT') -> int:
        return 0

    def gdo_filter(self, val: str) -> bool:
        """
        Return true when val matches this gdt and the row should be kept.
        """
        return True

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

    # Foo #
    def get_name(self):
        return self.__class__.__name__ + "#" + str(id(self))

    def name(self, name: str):
        return self

    def gdo_column_define(self) -> str:
        return ''

    def column_define_fk(self) -> str:
        return ''

    def is_primary(self) -> bool:
        return False

    def is_unique(self) -> bool:
        return False

    def gdo(self, gdo) -> Self:
        return self

    def val(self, val: str) -> Self:
        return self

    def value(self, value) -> Self:
        return self

    def initial(self, val: str | None):
        return self

    def get_initial(self):
        return None

    def get_val(self) -> str | None:
        return None

    def is_not_null(self) -> bool:
        return False

    def get_value(self):
        return None

    def get_test_vals(self) -> list[str]:
        return ['']

    def to_val(self, value) -> str:
        if value is None:
            return ''
        return str(value)

    def to_value(self, val: str):
        return val

    def dirty_vals(self) -> dict[str,str]:
        return {}

    def validate(self, val: str | None, value: any) -> bool:
        return True

    def validated(self):
        self.reset_error()
        if self.validate(self.get_val(), self.get_value()):
            return self

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

    def is_multiple(self) -> bool:
        return False

    def has_tooltip(self) -> bool:
        return False

    def get_tooltip_text(self) -> str:
        key = f"tt_{self.get_name()}"
        return t(key) if Trans.has(key) else ''

    def fields(self) -> list:
        return []

    def all_fields(self):
        return []

    def is_orderable(self) -> bool:
        return False

    def default_order(self) -> str:
        return 'ASC'

    def position(self, n: int):
        return self

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
        return self.render_method(mode)()

    @functools.cache
    def render_method(self, mode: Mode):
        return getattr(self, f'render_{mode.name.lower()}')

    def render_toml(self) -> str:
        return f"{self.get_name()} = \"{self.get_val() or ''}\"\n"

    def render_html(self) -> str:
        return self.get_val() or ''

    def render_json(self):
        return self.get_name()

    def render_telegram(self):
        return self.render_txt()

    def render_form(self) -> str:
        return ''

    def render_cell(self) -> str:
        return self.render_html()

    def render_cli(self) -> str:
        return self.render_txt()

    def render_txt(self) -> str:
        val = self.get_val()
        return val or ''

    def render_markdown(self):
        return self.render_txt()

    def render_irc(self) -> str:
        return self.render_txt()

    def render_val(self) -> str:
        return self.display_val(self.get_val())

    def render_suggestion(self) -> str:
        return ''

    def display_val(self, val: str) -> str:
        return val

    def copy(self):
        return self.copy_as(self.get_name())

    def copy_as(self, new_name: str) -> Self:
        cloned = deepcopy(self)
        return cloned.name(new_name)
