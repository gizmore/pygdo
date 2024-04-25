import json
from enum import Enum

from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.base.Util import jsn
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Template import GDT_Template
from gdo.core.WithLabel import WithLabel


class Encoding(Enum):
    ASCII = 1
    UTF8 = 2
    BINARY = 3


class GDT_String(WithLabel, GDT_Field):
    _encoding: Encoding
    _case_s: bool

    _minlen: int
    _maxlen: int
    _pattern: str

    _input_type: str

    def __init__(self, name):
        super(GDT_String, self).__init__(name)
        self._encoding = Encoding.UTF8
        self._hidden = False
        self._minlen = 0
        self._maxlen = 192
        self._pattern = ''
        self._case_s = False
        self._input_type = 'text'
        self.label(name)

    def minlen(self, minlen: int):
        self._minlen = minlen
        return self

    def maxlen(self, maxlen: int):
        self._maxlen = maxlen
        return self

    def case_s(self, case_s=True):
        self._case_s = case_s
        return self

    def case_i(self, case_i=True):
        self._case_s = not case_i
        return self

    def ascii(self):
        self._encoding = Encoding.ASCII
        return self

    def utf8(self):
        self._encoding = Encoding.UTF8
        return self

    def binary(self):
        self._encoding = Encoding.BINARY
        return self

    def gdo_column_define(self) -> str:
        return (f"{self._name} VARCHAR({self._maxlen}) "
                f"CHARSET {self.gdo_column_define_charset()} {self.gdo_column_define_collate()} "
                f"{self.gdo_column_define_default()} "
                f"{self.gdo_column_define_null()} ")

    def gdo_column_define_charset(self) -> str:
        match self._encoding:
            case Encoding.ASCII:
                return 'ascii'
            case Encoding.UTF8:
                return 'utf8mb4'
            case Encoding.BINARY:
                return 'binary'

    def gdo_column_define_collate(self) -> str:
        if self._encoding == Encoding.BINARY:
            return GDT.EMPTY_STRING
        append = '_general_ci'
        if self._case_s:
            append = '_bin'
        return f" COLLATE {self.gdo_column_define_charset()}{append}"

    ############
    # Validate #
    ############

    def validate(self, value):
        if not super().validate(value):
            return False
        if not self.validate_pattern(value):
            return False
        if not self.validate_length(value):
            return False
        return True

    def validate_pattern(self, value):
        return True

    def validate_length(self, value):
        return True

    ########
    # Util #
    ########

    def text(self, key: str, args: list[str] = None):
        return self.val(t(key, args))

    ##########
    # Render #
    ##########

    def render_txt(self):
        return self.get_val()

    def render_json(self):
        dic = {
            self.get_name(): self.get_val(),
        }
        return jsn(dic)

    def render_form(self):
        return GDT_Template.python('core', 'form_string.html', {'field': self})
