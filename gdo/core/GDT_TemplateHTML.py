from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.core.GDT_Template import GDT_Template


class GDT_TemplateHTML(GDT):

    CACHE: dict[str,dict[str,str]] = {}

    _tpl_module: str
    _tpl_path: str
    _tpl_args: dict[str,str]

    __slots__ = (
        '_tpl_module',
        '_tpl_path',
        '_tpl_args',
    )

    def __init__(self, module: str, path: str, args: dict[str,str]=None):
        super().__init__()
        self._tpl_module = module
        self._tpl_path = path
        self._tpl_args = args

    def get_html(self) -> str:
        if paths := self.CACHE.get(self._tpl_module):
            if html := paths.get(self._tpl_path):
                return html
        else:
            paths = self.CACHE[self._tpl_module] = {}
        with open(GDT_Template.get_path(self._tpl_module, self._tpl_path)) as fh:
            html = fh.read()
            paths[self._tpl_path] = html
            return html

    def get_replaced_html(self) -> str:
        html = self.get_html()
        for key, val in self._tpl_args.items():
            html = val.join(html.split(f"{{{{{key}}}}}"))
        return html

    ##########
    # Render #
    ##########

    def render_html(self) -> str:
        return self.get_replaced_html()

    def render_txt(self):
        return Strings.html_to_text(self.render_html())


def tplhtml(module: str, path: str, args: dict[str,str]=None):
    return GDT_TemplateHTML(module, path, args).render_html()
