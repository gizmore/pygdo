import functools

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import jsn
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_TemplateHTML import tplhtml
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
    def clear_assets(cls):
        cls._js = []
        cls._js_inline = ''
        cls._css = []
        cls._css_inline = ''

    @classmethod
    def instance(cls):
        return Application.get_page()

    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        self._title_bar = GDT_Bar('title').horizontal()
        self._top_bar = GDT_Container()
        self._left_bar = GDT_Bar('left').vertical()
        self._right_bar = GDT_Bar('right').vertical()
        self._bottom_bar = GDT_Container()

    def result(self, result: GDT):
        self._result = result
        return self

    def method(self, method: Method):
        self._method = method
        return self

    def render_txt(self) -> str:
        return self._result.render_txt()

    def render_html(self):
        return tplhtml('ui', 'page.html', {
            'lang': Application.LANG_ISO,
            'title': self._method.gdo_render_title(),
            'descr': self._method.gdo_render_descr(),
            'keywords': self._method.gdo_render_keywords(),
            'css': self.render_css(),
            'css_inline': self._css_inline,
            'js': self.render_js(),
            'js_inline': self._js_inline,
            'title_bar': self._title_bar.render_html(),
            'top_bar': self._top_bar.render_html(),
            'left_bar': self._left_bar.render_html(),
            'right_bar': self._right_bar.render_html(),
            'bottom_bar': self._bottom_bar.render_html(),
            'result': self._result.render(Mode.HTML),
        })

    @classmethod
    @functools.cache
    def render_js(cls) -> str:
        return "\n".join([f'<script src="{url}"></script>' for url in cls._js])

    @classmethod
    @functools.cache
    def render_css(cls) -> str:
        return "\n".join([f'<link rel="stylesheet" href="{url}" />' for url in cls._css])

    def render_json(self):
        return jsn({
            'code': Application.get_status_code(),
            'data': self._result.render_json(),
        })

    def init_sidebars(self):
        for module in ModuleLoader.instance().enabled():
            module.gdo_init_sidebar(self)
