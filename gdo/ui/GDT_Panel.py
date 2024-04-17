from gdo.base.GDT import GDT
from gdo.core.GDT_Template import tpl
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Panel(WithTitle, WithText, GDT):

    def __init__(self):
        super().__init__()

    def render_html(self):
        return tpl('ui', 'panel.html', {'field': self})
