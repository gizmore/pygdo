from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template
from gdo.ui.GDT_Bar import GDT_Bar


class GDT_Page(GDT):
    _result: GDT
    _method: Method

    _title_bar: GDT_Bar
    _top_bar: GDT_Container  # top response
    _left_bar: GDT_Bar
    _right_bar: GDT_Bar
    _bottom_bar: GDT_Container

    _js: list
    _js_inline: str
    _css: list

    @classmethod
    def instance(cls):
        return Application.get_page()

    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        self._js = []
        self._css = []
        self._js_inline = ''
        self._title_bar = GDT_Bar().horizontal()
        self._top_bar = GDT_Container()
        self._left_bar = GDT_Bar().vertical()
        self._right_bar = GDT_Bar().vertical()
        self._bottom_bar = GDT_Container()
        return self

    def result(self, result: GDT):
        self._result = result
        return self

    def method(self, method: Method):
        self._method = method
        return self

    def add_css(self, url: str):
        self._css.append(url)

    def render_html(self):
        return GDT_Template.python('ui', 'page.html', {'field': self})

