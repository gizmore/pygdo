from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.ui.WithText import WithText


class GDT_Trans(WithText, GDT):
    """
    A snippet of translated text.
    """
    def render(self, mode: Mode = Mode.html):
        return self.render_text(mode)
