from gdo.base.GDT import GDT
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import tpl
from gdo.ui.GDT_Icon import GDT_Icon
from gdo.ui.WithHREF import WithHREF


class GDT_Order(WithHREF, GDT_String):
    _order_multiple: bool

    def __init__(self, name):
        super().__init__(name)
        self._multiple = True
        self._order_multiple = True

    def no_multiple(self, no_multiple_order: bool = True):
        self._order_multiple = not no_multiple_order
        return self

    def display_table_order(self, gdt: GDT) -> str:
        if gdt.is_orderable():
            vals = {'field': self, 'gdt': gdt, 'GDT_Icon': GDT_Icon}
            return tpl('table', 'order_field.html', vals)
        else:
            return ''

    def href_order(self, gdt: GDT):
        return 'xxx'

