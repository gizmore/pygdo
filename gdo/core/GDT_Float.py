import sys

from gdo.core.GDT_String import GDT_String


class GDT_Float(GDT_String):
    _min: float
    _max: float

    def __init__(self, name: str):
        super().__init__(name)
        self._min = -sys.maxsize - 1
        self._max = sys.maxsize

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

#######
# GDO #
#######

    def to_value(self, val: str):
        if val is None:
            return None
        return float(val)

    def gdo_column_define(self) -> str:
        return f"{self._name} DOUBLE {self.gdo_column_define_null()} {self.gdo_column_define_default()}"

############
# Validate #
############

    def validate(self, value):
        if not super().validate(value):
            return False
        return self.validate_min_max(value)

    def validate_min_max(self, value):
        if value < self._min:
            return self.error('err_int_min', [self._min])
        if value > self._max:
            return self.error('err_int_max', [self._max])
        return True

##########
# Render #
##########
