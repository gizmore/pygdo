"""A CSS-style pixel or percentage length, resolved in an explicit context."""
import re

from gdo.core.GDT_String import GDT_String


class GDT_CSSLength(GDT_String):
    _LENGTH = re.compile(r'^([+-]?(?:\d+(?:\.\d+)?|\.\d+))(px|%)$', re.I)

    def __init__(self, name: str):
        super().__init__(name)
        self.maxlen(32)

    @classmethod
    def resolve(cls, value: str, reference: float) -> float:
        match = cls._LENGTH.fullmatch(value.strip()) if isinstance(value, str) else None
        if not match:
            raise ValueError('Expected a CSS length in px or %')
        number = float(match.group(1))
        return number * reference / 100 if match.group(2) == '%' else number

    def validate(self, val: str | None) -> bool:
        if not super().validate(val):
            return False
        if val is None:
            return True
        if not self._LENGTH.fullmatch(val.strip()):
            return self.error('err_css_length')
        return True
