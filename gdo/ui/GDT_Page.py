from gdo.base.GDT import GDT
from gdo.core.GDT_Template import GDT_Template


class GDT_Page(GDT):

    def __init__(self):
        super().__init__()

    def render_html(self):
        return GDT_Template.python('ui', 'page.html', {'page': self})
