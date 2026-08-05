from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Util import Strings


class GDT_Glyph(GDT):
    """A literal inline text fragment used to compose rendered messages."""

    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def render(self, mode: Mode = Mode.render_html):
        return Strings.html(self._text, mode)
