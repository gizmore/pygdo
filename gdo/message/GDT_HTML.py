from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Util import Strings


class GDT_HTML(GDT):

    _html: str

    def __init__(self):
        super().__init__()
        self._html = ''

    def gdo_redis_fields(self) -> list[str]:
        return [
            '_html',
        ]

    def gdo_wake_up(self):
        self._html = ''

    def text(self, text: str):
        return self.html(Strings.html(text, Mode.render_html))

    def html(self, html: str) -> 'GDT_HTML':
        self._html = html
        return self

    def render_txt(self) -> str:
        return Strings.html_to_text(self._html)

    def render_html(self) -> str:
        return self._html

    def render_cli(self) -> str:
        return self.render_txt()

    def render_irc(self) -> str:
        return self.render_txt()
