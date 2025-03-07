from gdo.core.GDT_Field import GDT_Field


class WithProxy:
    _proxy: (GDT_Field, any)

    def proxy(self, gdt: GDT_Field):
        self._proxy = gdt
        self._name = gdt.get_name()
        return self

    def get_name(self) -> str:
        return self._proxy.get_name()

    def not_null(self, notnull=True):
        self._proxy.not_null(notnull)
        return super().not_null(notnull)

    def is_not_null(self) -> bool:
        return self._proxy.is_not_null()

    # def get_val(self):
    #     return self._proxy.get_val()
    #
    # def get_value(self):
    #     return self._proxy.get_value()
