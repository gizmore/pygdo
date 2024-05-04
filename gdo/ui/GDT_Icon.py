from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.ui.WithIcon import WithIcon


class GDT_Icon(WithIcon, GDT):

    def __init__(self, name: str, alt: str = None, color: str = None, size: str = None):
        super().__init__()
        self.icon_name(name)
        self.icon_alt(alt or f"{name} icon")
        self.icon_color(color)
        self.icon_size(size)

    def render(self, mode: Mode = Mode.HTML):
        return self.render_icon(mode)
