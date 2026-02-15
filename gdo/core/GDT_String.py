import unicodedata
import regex
from enum import Enum

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.base.Util import jsn, dump, html
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
    _min_len: int
    _max_len: int
    _pattern: str
    _re_options: int
    _input_type: str
    _normalize: bool

    # __slots__ = (
    #     '_encoding',
    #     '_case_s',
    #     '_min_len',
    #     '_max_len',
    #     '_pattern',
    #     '_re_options',
    #     '_input_type',
    # )

    def __init__(self, name: str = None):
        super().__init__(name)
        self._encoding = Encoding.UTF8
        self._hidden = False
        self._min_len = 0
        self._max_len = 192
        self._pattern = self.EMPTY_STR
        self._re_options = 0
        self._case_s = False
        self._input_type = 'text'
        self._normalize = False
        if name:
            self.label(name)

    def is_orderable(self) -> bool:
        return True

    ##############
    # Attributes #
    ##############
    def minlen(self, minlen: int):
        self._min_len = minlen
        return self

    def maxlen(self, maxlen: int):
        self._max_len = maxlen
        return self

    def normalize(self, normalize: bool = True):
        self._normalize = normalize
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
        return self.case_i(bool(options & regex.IGNORECASE))

    def val(self, val: str | list):
        if type(val) is str and not self._multiple:
            if self._normalize:
                return super().val(self.utf8_normalize(val))
        return super().val(val)

    def get_test_vals(self) -> list[str|None]:
        return ['<script>']

    #######
    # DBA #
    #######

    def gdo_varchar_define(self) -> str:
        return 'VARCHAR'

    def gdo_column_define(self) -> str:
        return (f"{self._name} {self.gdo_varchar_define()}({self._max_len}) "
                f"CHARSET {self.gdo_column_define_charset()} {self.gdo_column_define_collate()} "
                f"{self.gdo_column_define_default()} "
                f"{self.gdo_column_define_null()} ")

    def gdo_column_define_charset(self) -> str:
        match self._encoding:
            case Encoding.UTF8:
                return 'utf8mb4'
            case Encoding.ASCII:
                return 'ascii'
            case _:
                return 'binary'

    def gdo_column_define_collate(self) -> str:
        if self._encoding == Encoding.BINARY:
            return self.EMPTY_STR
        append = '_bin' if self._case_s else '_general_ci'
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

    def validate(self, val: str|None) -> bool:
        if not super().validate(val):
            return False
        elif not val:
            return True
        if not self.validate_pattern(val):
            return False
        if not self.validate_length(val):
            return False
        return True

    def validate_pattern(self, val: str):
        if self._pattern:
            if not regex.match(self._pattern, val, flags=self._re_options):
                return self.error('err_str_pattern',(html(self._pattern, Application.get_mode()),))
        return True

    def validate_length(self, val: str):
        l = len(val)
        if self._min_len and l < self._min_len:
            return self.error('err_str_min_len', (self._min_len,))
        if self._max_len and l > self._max_len:
            return self.error('err_str_max_len', (self._max_len,))
        return True

    ########
    # Util #
    ########

    def text(self, key: str, args: tuple[any, ...] = None):
        return self.val(t(key, args))

    def utf8_normalize(self, val: str) -> str:
        return unicodedata.normalize('NFC', val)

    @staticmethod
    def utf8_transcribe(s: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFKD', s)
            if not unicodedata.combining(c)
        )

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
        return {
            self.get_name(): self.get_val(),
        }

    def render_form(self):
        if self.is_hidden():
            return GDT_Hidden(self._name).val(self._val).render_form()
        return GDT_Template.python('core', 'form_string.html', {'field': self})

    def render_irc(self) -> str:
        return str(self.get_val())

    def render_toml(self) -> str:
        tt = self.render_tooltip() if self.has_tooltip() else ''
        return f"{self.get_name()} = \"{self.get_val() or ''}\" # {tt} {self.render_suggestion()}\n"

    def render_list(self) -> str:
        return self.render_html()

    def display_val(cls, val: str) -> str:
        return html(val, Application.get_mode())
