from gdo.base.Render import Mode
from gdo.core.GDT_Field import GDT_Field


class WithProxy:

    _proxy: GDT_Field

    def proxy(self, gdt: GDT_Field):
        self._proxy = gdt
        return self

    def get_name(self) -> str:
        return self._proxy.get_name()

    def not_null(self, notnull=True):
        self._proxy.not_null(notnull)
        return self

    def val(self, val: str):
        self._proxy.val(val)
        return self

    def get_val(self):
        return self._proxy.get_val()

    def validate(self, value: any) -> bool:
        return self._proxy.validate(value)

    def render(self, mode: Mode):
        return self._proxy.render(mode)
