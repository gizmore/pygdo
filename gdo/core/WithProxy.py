from gdo.core.GDT_Field import GDT_Field

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.base.GDO import GDO

class WithProxy:
    _proxy: GDT_Field

    __slots__ = (
        '_proxy',
    )

    def proxy(self, gdt: GDT_Field):
        self._proxy = gdt
        self._name = gdt.get_name()
        return self

    def render_suggestion(self) -> str:
        return self._proxy.render_suggestion()

    def not_null(self, notnull=True):
        self._proxy.not_null(notnull)
        return super().not_null(notnull)

    def is_not_null(self) -> bool:
        return self._proxy.is_not_null()

    def render_label(self):
        return self._proxy.render_label()

    def render_val(self) -> str:
        return self._proxy.render_val()

    def render_cell(self) -> str:
        return self._proxy.render_cell()

    def val(self, val: str):
        self._proxy.val(val)
        return self

    def get_val(self):
        return self._proxy.get_val()

    def get_value(self):
        return self._proxy.get_value()

    def to_value(self, val: str):
        return self._proxy.to_value(val)

    def to_val(self, value):
        return self._proxy.to_val(value)

    def render_html(self):
        self._proxy.render_html()

    def gdo(self, gdo: 'GDO'):
        self._proxy.gdo(gdo)
        return self
