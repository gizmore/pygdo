from gdo.base.GDT import GDT
from gdo.base.Render import Mode


class GDT_Newline(GDT):

    def render(self, mode: Mode = Mode.html):
        if mode == Mode.html:
            return "<br/>"
        return "\n"

    def render_markdown(self):
        return "\n\n"
