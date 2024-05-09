from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Util import Strings, dump
from gdo.base.WithError import WithError
from gdo.core.WithGDO import WithGDO
from gdo.ui.WithIcon import WithIcon
from gdo.ui.WithTooltip import WithTooltip


class GDT_Field(WithGDO, WithTooltip, WithIcon, WithError, GDT):
    _name: str
    _not_null: bool
    _val: str
    _initial: str
    _converted: bool
    _primary: bool
    _unique: bool
    _writable: bool
    _hidden: bool
    _positional: bool | None
    _multiple: bool

    def __init__(self, name):
        super(GDT_Field, self).__init__()
        self._name = name
        self._not_null = False
        self._val = ''
        self._initial = ''
        self._primary = False
        self._value = None
        self._converted = False
        self._unique = False
        self._writable = True
        self._hidden = False
        self._positional = None
        self._multiple = False

    def get_name(self):
        return self._name

    def get_val(self):
        if not self._val:
            return None
        return self._val

    def get_value(self):
        if not self._converted:
            self._value = self.to_value(self.get_val())
            self._converted = True
        return self._value

    def val(self, val: str | list):
        self._val = val[0] if isinstance(val, list) and not self._multiple else val
        self._converted = False
        return self

    def value(self, value):
        self._converted = True
        self._value = value
        self._val = self.to_val(value)
        return self

    def gdo(self, gdo: GDO):
        self._gdo = gdo
        return self.val(gdo.gdo_val(self._name))

    def initial(self, val: str):
        self._initial = val
        return self.val(val)

    def initial_value(self, value: any):
        return self.initial(self.to_val(value))

    def is_primary(self) -> bool:
        return self._primary

    def is_unique(self) -> bool:
        return self._unique

    def primary(self, primary=True):
        self._primary = primary
        return self.not_null()

    def unique(self, unique=True):
        self._unique = unique
        return self

    def multiple(self, multiple: bool = True):
        self._multiple = multiple
        return self

    def positional(self, positional: bool = True):
        self._positional = positional
        return self

    def is_positional(self) -> bool:
        if self._positional is not None:
            return self._positional
        return self._not_null and not self._initial

    def is_not_null(self) -> bool:
        return self._not_null

    def writable(self, writable: bool = True):
        self._writable = writable
        return self

    def is_writable(self) -> bool:
        return self._writable

    def hidden(self, hidden: bool = True):
        self._hidden = hidden
        return self

    def is_hidden(self) -> bool:
        return self._hidden

    def get_initial(self):
        return self._initial

    def gdo_column_define_null(self) -> str:
        if self._not_null:
            return ' NOT NULL'
        return ''

    def gdo_column_define_default(self) -> str:
        if self._initial != '':
            return " DEFAULT " + self.quote(self._initial)
        return GDT.EMPTY_STRING

    def not_null(self, not_null: bool = True):
        self._not_null = not_null
        return self

    def nullable(self, nullable: bool = True):
        return self.not_null(not nullable)

    def error(self, errkey, errargs=None):
        if errargs is None:
            errargs = []
        self._errkey = errkey
        self._errargs = errargs
        return False

    ############
    # Validate #
    ############

    def validate(self, value: any) -> bool:
        if value is None:
            if self._not_null:
                return self.error('err_not_null')

        if self._unique and not self.validate_unique(value):
            return False

        return True

    def validate_unique(self, value):
        self._gdo.table().select()

    ##########
    # Render #
    ##########
    # def render_val(self):
    #     if isinstance(self._val, list):
    #         dump(self)
    #     return Strings.html(self._val)

    # def render_html(self) -> str:
    #     return Strings.html(self._val)
    #
    # def render_cli(self) -> str:
    #     return self._val
