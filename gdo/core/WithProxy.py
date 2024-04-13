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
