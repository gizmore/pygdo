import sys

from gdo.base.Util import NumericUtil
from gdo.core.GDT_String import GDT_String


class GDT_Int(GDT_String):
    _min: int
    _max: int
    _bytes: int
    _signed: bool
    _base: int

    def __init__(self, name: str):
        super().__init__(name)
        self._signed = True
        self._bytes = 4
        self._min = -sys.maxsize - 1
        self._max = sys.maxsize
        self._base = 10

    def is_orderable(self) -> bool:
        return True

    #######
    # GDT #
    #######
    # def val(self, val: str | list):
    #     if self._multiple:
    #         return super().val(val)
    #     if val is None:
    #         return None
    #     return super().val(val)

    ##############
    # Attributes #
    ##############

    def min(self, minval: int = None):
        self._min = minval
        return self

    def max(self, maxval: int = None):
        self._max = maxval
        return self

    def bytes(self, _bytes: int):
        self._bytes = _bytes
        return self

    def signed(self, signed: bool = True):
        self._signed = signed
        return self

    def unsigned(self, unsigned: bool = True):
        self._signed = not unsigned
        return self

    def base(self, base: int):
        self._base = base
        return self

    def get_test_vals(self) -> list[str|None]:
        return ['4']

    #######
    # GDO #
    #######

    def gdo_filter(self, val: str) -> bool:
        return self.get_val() == val

    def to_value(self, val: str):
        if val is None:
            return None
        return int(val)

    def gdo_column_define_size(self):
        match self._bytes:
            case 1:
                return 'TINY'
            case 2:
                return 'MEDIUM'
            case 8:
                return 'BIG'
            case _:
                return ''

    def gdo_column_define_sign(self):
        if not self._signed:
            return 'UNSIGNED'
        return ''

    def gdo_column_define(self) -> str:
        return (f"{self._name} {self.gdo_column_define_size()}INT {self.gdo_column_define_sign()}"
                f" {self.gdo_column_define_null()} {self.gdo_column_define_default()}")

    ############
    # Validate #
    ############

    def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
            return False
        if value is None:
            return True
        return self.validate_min_max(value)

    def validate_min_max(self, value):
        if value < self._min:
            return self.error('err_int_min', (self._min,))
        if value > self._max:
            return self.error('err_int_max', (self._max,))
        return True

    ##########
    # Render #
    ##########
    # def render_toml(self) -> str:
    #     prefix = NumericUtil.output_prefix(self._base)
    #     return f"{self.get_name()} = {prefix}{self.get_val()}\n"
    #
    # def getBasePrefix(self):
    #     pass
