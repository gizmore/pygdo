from gdo.core.GDT_Field import GDT_Field


class WithProxy:
    _proxy: (GDT_Field, any)

    __slots__ = (
        '_proxy',
    )

    def proxy(self, gdt: GDT_Field):
        self._proxy = gdt
        self._name = gdt.get_name()
        return self

    def not_null(self, notnull=True):
        self._proxy.not_null(notnull)
        return super().not_null(notnull)

    def is_not_null(self) -> bool:
        return self._proxy.is_not_null()
