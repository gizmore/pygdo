import sys

from gdo.base.Trans import t
from gdo.core.GDT_String import GDT_String


class GDT_Float(GDT_String):
    _precision: int
    _fill_zeroes: bool
    _no_thousands: bool
    _min: float
    _max: float

    def __init__(self, name: str):
        super().__init__(name)
        self._min = -sys.maxsize - 1
        self._max = sys.maxsize
        self._precision = 3
        self._fill_zeroes = False
        self._no_thousands = False

    ##############
    # Attributes #
    ##############

    def min(self, minval: float = None):
        if minval is None:
            delattr(self, '_min')
        else:
            self._min = minval
        return self

    def max(self, maxval: float = None):
        if maxval is None:
            delattr(self, '_max')
        else:
            self._max = maxval
        return self

    def precision(self, precision: int):
        self._precision = precision
        return self

    def fill_zeroes(self, fill_zeroes: bool = True):
        self._fill_zeroes = fill_zeroes
        return self

    def no_thousands(self, no_thousands: bool = True):
        self._no_thousands = no_thousands
        return self

    #######
    # GDO #
    #######

    def to_value(self, val: str):
        if val is None:
            return None
        return float(val)

    def gdo_column_define(self) -> str:
        return f"{self._name} DOUBLE{self.gdo_column_define_null()}{self.gdo_column_define_default()}"

    ############
    # Validate #
    ############

    def validate(self, value):
        if not super().validate(value):
            return False
        return self.validate_min_max(value)

    def validate_min_max(self, value):
        if self._min is not None and value < self._min:
            return self.error('err_int_min', [self._min])
        if self._max is not None and value > self._max:
            return self.error('err_int_max', [self._max])
        return True

    ##########
    # Render #
    ##########
    @staticmethod
    def display_float(f: float, precision: int, no_thousands: bool = False, fill_zeroes: bool = False):
        ts = t('thousands_sep')
        dp = t('decimal_point')
        fs = "{:"
        fs += "" if no_thousands else ","
        fs += '.'
        fs += "0" if fill_zeroes else ""
        fs += str(precision)
        fs += "f}"
        formatted = (fs.format(f).
                     replace(",", "temp").
                     replace(".", dp).
                     replace("temp", ts))
        if not fill_zeroes:
            formatted = formatted.rstrip('0').rstrip(dp)
        return formatted

    def render_txt(self):
        return self.display_float(self.get_value(), self._precision, self._no_thousands, self._fill_zeroes)
