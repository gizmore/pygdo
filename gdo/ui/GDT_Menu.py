from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template


class GDT_Menu(GDT_Container):

    def __init__(self):
        super().__init__()

    def render(self, mode: Mode = Mode.render_html):
        if mode.is_html():
            return GDT_Template.python('ui', 'menu.html', {'field': self})
        return super().render(mode)
