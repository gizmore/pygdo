from gdo.base.GDT import GDT
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import tpl


class GDT_Filter(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.multiple()

    def display_table_filter(self, gdt: GDT) -> str:
        vals = {'field': self, 'gdt': gdt}
        if isinstance(gdt, GDT_String):
            return tpl('table', 'filter_string.html', vals)

    def filter_value(self, gdt: GDT):
        return ''