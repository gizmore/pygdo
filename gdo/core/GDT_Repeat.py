from gdo.core.GDT_Field import GDT_Field
from gdo.core.WithProxy import WithProxy


class GDT_Repeat(WithProxy, GDT_Field):

    def __init__(self, proxy: GDT_Field):
        super().__init__(proxy.get_name())
        self.proxy(proxy)

    def is_positional(self) -> bool:
        return True

    def val(self, val: str | list):
        self._val = val
        self._converted = False
        return self

    def to_val(self, values: list):
        if values is None:
            return None
        vals = []
        for value in values:
            vals.append(self._proxy.to_val(value))
        return vals

    def to_value(self, vals: list[str]):
        if vals is None:
            return None
        values = []
        for val in vals:
            values.append(self._proxy.to_value(val))
        return values

    def validate(self, values):
        if values is None:
            return self._proxy.validate(values)
        for value in values:
            if not self._proxy.validate(value):
                self.error(self._proxy._errkey, self._proxy._errargs)
                return False
        return True

    def render_cli(self) -> str:
        out = ""
        for val in self.get_val():
            out += val
        return out
