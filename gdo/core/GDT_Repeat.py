import sys

from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.WithProxy import WithProxy


class GDT_Repeat(WithProxy, GDT_UInt):

    def __init__(self, proxy: GDT_Field):
        super().__init__(proxy.get_name())
        self.proxy(proxy)
        self._min = 1 if proxy._not_null else 0
        self._max = sys.maxsize

    def is_positional(self) -> bool:
        return True

    def is_multiple(self) -> bool:
        return True

    def val(self, val: str | list):
        self._val = val
        self._converted = False
        return self

    def to_val(self, values: list):
        if not values:
            return None
        vals = []
        for value in values:
            val = self._proxy.to_val(value)
            if val is not None:
                vals.append(val)
        return vals if vals else None

    def to_value(self, vals: list[str]):
        if vals is None:
            return None
        values = []
        for val in vals:
            value = self._proxy.to_value(val)
            if value is not None:
                values.append(value)
        return values

    def validate(self, val: str | None, values: any) -> bool:
        if values is None:
            if not self._proxy.validate(val, values):
                return self.error(self._proxy._errkey, self._proxy._errargs)
            return super().validate(val, None)
        if not self.validate_min_max(len(values)):
            return False
        for value in values:
            if not self._proxy.validate(val, value):
                return self.error(self._proxy._errkey, self._proxy._errargs)
        return True

    def validate_min_max(self, value):
        if value < self._min:
            return self.error('err_repeat_min', (self._min,))
        if value > self._max:
            return self.error('err_repeat_max', (self._max,))
        return True

    def render_cli(self) -> str:
        out = ""
        for val in self.get_val():
            out += val
        return out

    def render_form(self) -> str:
        proxy_key = self._name + '[]'
        out = ''
        vals = self.get_val()
        if vals is not None:
            for val in vals:
                out += self._proxy.not_null(False).name(proxy_key).val(val).render_form()
        out += self._proxy.val('').render_form()
        return out
