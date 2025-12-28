from gdo.base.GDT import GDT
from gdo.base.GDO import GDO
from gdo.base.Query import Query
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import tpl
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.table.MethodTable import MethodTable


class GDT_Filter(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.multiple()

    def display_table_filter(self, gdt: GDT) -> str:
        vals = {'field': self, 'gdt': gdt}
        if isinstance(gdt, GDT_String):
            return tpl('table', 'filter_string.html', vals)
        return GDO.EMPTY_STR

    def filter_query(self, query: Query, method: 'MethodTable'):
        pass


    def filter_value(self, gdt: GDT):
        return ''