import sys
from html import escape

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time


class GDT_Duration(GDT_String):
    _units: int
    _with_millis: bool
    _min: float
    _max: float

    def __init__(self, name):
        super().__init__(name)
        self.icon('clock')
        self._units = 2
        self._with_millis = False
        self._min = 0.0
        self._max = sys.maxsize

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

    def countdown_until(self, timestamp: float, ended_text: str = 'Ended'):
        """Render a duration counting down to an absolute Unix timestamp."""
        self._countdown_until = float(timestamp)
        self._countdown_ended_text = ended_text
        return self

    def to_val(self, value):
        if value is None:
            return None
        return Time.human_duration(value, self._units, self._with_millis)

    def to_value(self, val: str):
        if not val:
            return 0
        return Time.human_to_seconds(val)

    def render(self, mode: Mode = Mode.render_html):
        if mode == Mode.render_form:
            return super().render(mode)
        if hasattr(self, '_countdown_until'):
            remaining = max(0, self._countdown_until - Application.TIME)
            value = (Time.human_duration(remaining, self._units) if remaining > 0
                     else self._countdown_ended_text)
            if mode in (Mode.render_html, Mode.render_cell):
                ended = escape(self._countdown_ended_text, quote=True)
                return (f'<span class="gdt-duration-countdown" data-countdown-until="{self._countdown_until}" '
                        f'data-countdown-units="{self._units}" data-countdown-ended="{ended}">{escape(value)}</span>')
            return value
        return Time.human_duration(self.get_value(), self._units)

    def validate(self, val: str|None) -> bool:
        if not super().validate(val):
            return False
        value = self.get_value()
        if value < self._min:
            return self.error('err_int_min', (self._min,))
        if self._max is not None and value > self._max:
            return self.error('err_int_max', (self._max,))
        return True
