from gdo.base.GDT import GDT
from gdo.core.GDT_Template import GDT_Template


class GDT_Page(GDT):
    _result: GDT

    def __init__(self):
        super().__init__()

    def render_html(self):
        return GDT_Template.python('ui', 'page.html', {'field': self})

    def result(self, result: GDT):
        self._result = result
        return self
