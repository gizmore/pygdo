from gdo.base.GDT import GDT
from gdo.base.GDO import GDO
from gdo.base.Query import Query
from gdo.core.GDT_Bool import GDT_Bool
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
        return gdt.render_table_filter(vals)

    def filter_query(self, query: Query, method: 'MethodTable'):
        for gdt in method.gdo_table_headers():
            if gdt.is_filterable():
                if values := self.filter_values(gdt):
                    gdt.val(values).gdo_filter_query(method.gdo_table(), query)
                elif val := self.filter_value(gdt):
                    gdt.val(val).gdo_filter_query(method.gdo_table(), query)

    def filter_values(self, gdt: GDT) -> dict[str, str]:
        try:
            values = self.get_val().get(gdt.get_name())
            if not isinstance(values, dict):
                return {}
            return {
                key: value[0] if isinstance(value, list) and value else value
                for key, value in values.items()
                if value
            }
        except Exception:
            return {}

    def filter_value(self, gdt: GDT):
        try:
            value = self.get_val().get(gdt.get_name())
            return value[0] if isinstance(value, list) else ''
        except Exception:
            return ''

    def filter_date_value(self, gdt: GDT, key: str) -> str:
        return self.filter_values(gdt).get(key, '')

    def html_selected(self, gdt: GDT, val: str):
        return ' selected="selected"' if self.filter_value(gdt) == val else ''
