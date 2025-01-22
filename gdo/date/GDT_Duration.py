from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time


class GDT_Duration(GDT_String):
    _units: int
    _with_millis: bool
    _min: float
    _max: float

    def __init__(self, name):
        super().__init__(name)
        self._units = 2
        self._with_millis = False
        self._min = 0.0
        self._max = None

    def units(self, units: int, with_millis: bool = True):
        self._units = units
        self._with_millis = with_millis
        return self

    def min(self, min: float):
        self._min = min
        return self

    def max(self, max: float):
        self._max = max
        return self

    def to_val(self, value):
        if value is None:
            return None
        return Time.human_duration(value)

    def to_value(self, val: str):
        if val is None:
            return None
        return Time.human_to_seconds(val)

    def render_html(self) -> str:
        return Time.human_duration(self.get_value(), self._units)

    def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
            return False
        if value < self._min:
            return self.error('err_int_min', (self._min,))
        if self._max is not None and value > self._max:
            return self.error('err_int_max', (self._max,))
        return True
