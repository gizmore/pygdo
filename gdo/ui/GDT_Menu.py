from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template


class GDT_Menu(GDT_Container):

    def __init__(self):
        super().__init__()

    def render_form(self):
        return GDT_Template.python('ui', 'menu.html', {'field': self})

    def render_html(self):
        return GDT_Template.python('ui', 'menu.html', {'field': self})
