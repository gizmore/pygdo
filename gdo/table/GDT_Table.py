from enum import Enum

from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Result import Result
from gdo.base.WithName import WithName
from gdo.core.GDT_Template import GDT_Template
from gdo.form.GDT_Form import GDT_Form


class TableMode(Enum):
    TABLE = 1
    LIST = 2
    CARDS = 3


class GDT_Table(WithName, GDT):
    _table_result: Result
    _table_method: object
    _table_mode: TableMode

    def __init__(self, name: str = "table"):
        super().__init__()
        self.name(name)
        self._table_mode = TableMode.TABLE

    ##############
    # Attributes #
    ##############
    def result(self, result: Result):
        self._table_result = result
        return self

    def method(self, method: object):
        self._table_method = method
        return self

    def mode(self, mode: TableMode):
        self._table_mode = mode
        return self

    ##########
    # Render #
    ##########
    def render_html(self) -> str:
        vals = {'field': self, 'method': self._table_method}
        filename = f"{self._table_mode.name.lower()}.html"
        return GDT_Template.python('table', filename, vals)

    def render_cli(self) -> str:
        return self.render_textual(Mode.CLI)

    def render_txt(self) -> str:
        return self.render_textual(Mode.TXT)

    def render_textual(self, mode: Mode):
        method = self._table_method
        result = method.gdo_table_result()
        out = []
        for gdo in result:
            out.append(method.gdo(gdo).render(mode))
        return method.gdo_render_title() + ': ' + ", ".join(out)
