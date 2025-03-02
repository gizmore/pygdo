import unicodedata
from enum import Enum

from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.base.Util import jsn, dump
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Template import GDT_Template
from gdo.form.GDT_Hidden import GDT_Hidden


class Encoding(Enum):
    ASCII = 1
    UTF8 = 2
    BINARY = 3


class GDT_String(GDT_Field):
    _encoding: Encoding
    _case_s: bool

    _minlen: int
    _maxlen: int
    _pattern: str
    _re_options: int

    _input_type: str

    def __init__(self, name):
        super(GDT_String, self).__init__(name)
        self._encoding = Encoding.UTF8
        self._hidden = False
        self._minlen = 0
        self._maxlen = 192
        self._pattern = ''
        self._re_options = 0
        self._case_s = False
        self._input_type = 'text'
        self.label(name)

    def is_orderable(self) -> bool:
        return True

    ##############
    # Attributes #
    ##############
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

    def pattern(self, pattern: str, options: int = 0):
        self._pattern = pattern
        self._re_options = options
        return self

    def val(self, val: str | list):
        if self._multiple:
            return super().val(val)
        if val is None:
            return None
        if type(val) is str:
            return super().val(self.utf8_normalize(val))
        return super().val(val)

    def get_test_vals(self) -> list[str|None]:
        return ['<script>']

    #######
    # DBA #
    #######

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
            return ''
        append = '_general_ci'
        if self._case_s:
            append = '_bin'
        return f" COLLATE {self.gdo_column_define_charset()}{append}"

    def gdo_compare(self, gdt: GDT) -> int:
        s1, s2 = self.get_value(), gdt.get_value()
        if s2 is None and s1:
            return 1
        if s1 is None and s2:
            return -1
        if s1 and s2:
            return (s1 > s2) - (s1 < s2)
        return 0

    def gdo_filter(self, val: str) -> bool:
        return self.get_val().index(val) >= 0

    ############
    # Validate #
    ############

    def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
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

    def text(self, key: str, args: tuple[any] = None):
        return self.val(t(key, args))

    def utf8_normalize(self, val: str) -> str:
        return unicodedata.normalize('NFC', val)

    ##########
    # Render #
    ##########

    def html_readonly(self) -> str:
        if not self.is_writable():
            return ' readonly="readonly"'
        return ''

    def html_required(self):
        if self.is_not_null():
            return ' required="required"'
        return ''

    def html_pattern(self):
        if self._pattern:
            p = self._pattern.strip('^$')
            return f' pattern="{p}"'
        return ''

    def render_json(self):
        dic = {
            self.get_name(): self.get_val(),
        }
        return jsn(dic)

    def render_form(self):
        if self.is_hidden():
            return GDT_Hidden(self._name).val(self._val).render_form()
        return GDT_Template.python('core', 'form_string.html', {'field': self})

    def render_irc(self) -> str:
        return str(self.get_val())
