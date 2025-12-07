import re

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import tpl
from gdo.ui.GDT_Icon import GDT_Icon
from gdo.ui.WithHREF import WithHREF


class GDT_Order(WithHREF, GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self._multiple = True

    def display_table_order(self, gdt: GDT) -> str:
        if gdt.is_orderable():
            vals = {'field': self, 'gdt': gdt, 'GDT_Icon': GDT_Icon}
            return tpl('table', 'order_field.html', vals)
        else:
            return ''

    def order_query(self, query: Query):
        vals = self.get_val()
        if vals is not None:
            for val in vals:
                query.order(val)

    def get_order_dict(self) -> dict[str, str]:
        if val := self.get_val():
            return {key: direction for key, direction in (s.split() for s in val)}
        else:
            return {}

    def href_order(self, gdt: GDT, dir: str):
        url = Application.current_href()
        find = f"&{self.get_name()}={gdt.get_name()}"
        repl = f"&{self.get_name()}={gdt.get_name()}%20{dir}"
        if url.find(f"{find}%20{dir}") >= 0:
            url = re.sub(f"&{self.get_name()}={gdt.get_name()}%20{dir}", '', url)
        elif url.find(find) >= 0:
            url = re.sub(f"&{self.get_name()}={gdt.get_name()}%20(ASC|DESC)", repl, url)
        else:
            url += f"&{self.get_name()}={gdt.get_name()}%20{dir}"
        return url

    def html_selected(self, gdt: GDT, dir: str):
        url = Application.current_href()
        find = f"&{self.get_name()}={gdt.get_name()}%20{dir}"
        if url.find(find) >= 0:
            return ' class="active"'
        return ''

