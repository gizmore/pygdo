from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template
from gdo.ui.GDT_Bar import GDT_Bar


class GDT_Page(GDT):
    _js: list[str] = []
    _js_inline: str = ''
    _css: list[str] = []
    _css_inline: str = ''

    _result: GDT
    _method: Method

    _title_bar: GDT_Bar
    _top_bar: GDT_Container  # top response
    _left_bar: GDT_Bar
    _right_bar: GDT_Bar
    _bottom_bar: GDT_Container

    @classmethod
    def instance(cls):
        return Application.get_page()

    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        # self._js = []
        # self._css = []
        # self._js_inline = ''
        # self._css_inline = ''
        self._title_bar = GDT_Bar().horizontal()
        self._top_bar = GDT_Container()
        self._left_bar = GDT_Bar('left').vertical()
        self._right_bar = GDT_Bar('right').vertical()
        self._bottom_bar = GDT_Container()
        return self

    # def clear(self):
        # self._js.clear()
        # self._css.clear()
        # self._js_inline = ''
        # self._css_inline = ''
        # self._title_bar.clear()
        # self._top_bar.clear()
        # self._left_bar.clear()
        # self._right_bar.clear()
        # self._bottom_bar.clear()

    def result(self, result: GDT):
        self._result = result
        return self

    def method(self, method: Method):
        self._method = method
        return self

    def render_html(self):
        return GDT_Template.python('ui', 'page.html', {'field': self, 'result': self._result.render(Mode.HTML)})

    def render_json(self):
        return {
            'code': Application.get_status_code(),
            'data': self._result.render_json(),
        }

    @classmethod
    def clear_assets(cls):
        cls._js = []
        cls._js_inline = ''
        cls._css = []
        cls._css_inline = ''
