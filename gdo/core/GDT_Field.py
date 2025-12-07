from typing import Any

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.WithError import WithError
from gdo.core.WithGDO import WithGDO
from gdo.core.WithLabel import WithLabel
from gdo.core.WithNullable import WithNullable
from gdo.ui.WithIcon import WithIcon
from gdo.ui.WithTooltip import WithTooltip


class GDT_Field(WithGDO, WithLabel, WithTooltip, WithIcon, WithError, WithNullable, GDT):
    _name: str
    _val: str|None
    _value: Any
    _prev: str
    _initial: str|None
    _converted: bool
    _primary: bool
    _unique: bool
    _writable: bool
    _hidden: bool
    _secret: bool
    _positional: bool | None
    _position: int
    _multiple: bool

    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._not_null = False
        self._val = None
        self._initial = None
        self._primary = False
        self._value = None
        self._converted = False
        self._unique = False
        self._writable = True
        self._hidden = False
        self._positional = None
        self._position = -1
        self._multiple = False
        self._secret = False

    def get_name(self):
        return self._name

    def name(self, name: str):
        self._name = name
        return self

    def get_val(self):
        return None if not self._val else self._val

    def get_value(self):
        if not self._converted:
            self._value = self.to_value(self.get_val())
            self._converted = True
        return self._value

    def dirty_vals(self) -> dict[str,str]:
        return {self._name: self._val}

    def val(self, val: str | list):
        self._prev = self._val
        self._val = val[0] if type(val) is list and not self._multiple else val
        self._converted = False
        return self

    def value(self, value):
        self._converted = True
        self._value = value
        self._prev = self._val
        self._val = self.to_val(value)
        return self

    def gdo(self, gdo: GDO):
        self._gdo = gdo
        val = gdo._vals.get(self._name)
        self.val(val)
        if self._name in gdo._values:
            self._value = gdo._values.get(self._name)
            self._converted = True
        return self

    def initial(self, val: str):
        self._initial = val
        self._val = val
        return self #.val(val)

    def initial_value(self, value: any):
        return self.initial(self.to_val(value))

    def secret(self, secret: bool = True):
        self._secret = secret
        return self

    def is_secret(self) -> bool:
        return self._secret

    def is_primary(self) -> bool:
        return self._primary

    def is_unique(self) -> bool:
        return self._unique

    def primary(self, primary: bool=True):
        self._primary = primary
        return self.not_null()

    def unique(self, unique: bool=True):
        self._unique = unique
        return self

    def multiple(self):
        self._multiple = True
        return self

    def positional(self, positional: bool|None = True):
        self._positional = positional
        return self

    def position(self, n: int):
        self._position = n
        return self

    def is_positional(self) -> bool:
        if self._positional is not None:
            return self._positional
        return self._not_null and not self._initial

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
        if self._initial is not None:
            return " DEFAULT " + self.quote(self._initial)
        return ''

    def error(self, errkey: str, errargs: tuple[str|int|float,...] = None) -> bool:
        self._errkey = errkey
        self._errargs = errargs
        return False

    def is_multiple(self) -> bool:
        return self._multiple

    ############
    # Validate #
    ############

    def validate(self, val: str|None) -> bool:
        if not self.validate_null(val):
            return False
        if self._unique and not self.validate_unique(val):
            return False
        return True

    def validate_unique(self, val: str):
        if self._gdo.table().get_by_vals({self._name: val}):
            return self.error_unique()
        return True

    def error_unique(self):
        return self.error('err_not_unique')

    ##########
    # Render #
    ##########
    def html_placeholder(self) -> str:
        if self.has_tooltip():
            return f' placeholder="{self.render_tooltip()}"'
        elif self.has_label():
            return f' placeholder="{self.render_label()}"'
        else:
            return ''

    def render_json(self):
        return self.get_val()

    def render_card(self) -> str:
        return "<p>" + self.render_label() + ": "  + (self.render_val() or Render.italic(t('none'))) + '</p>'
