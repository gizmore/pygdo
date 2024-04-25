from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time


class GDT_Duration(GDT_String):
    _units: int
    _with_millis: bool

    def __init__(self, name):
        super().__init__(name)
        self._units = 2

    def units(self, units: int, with_millis: bool = True):
        self._units = units
        self._with_millis = with_millis
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
