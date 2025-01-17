from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import tpl, GDT_Template
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle



class GDT_Panel(WithTitle, WithText, GDT_Container):

    def __init__(self):
        super().__init__()

    def render_super_fields(self, mode: Mode = Mode.HTML):
        return super().render_fields(mode)

    def render_fields(self, mode: Mode = Mode.HTML):
        if mode == Mode.HTML:
            return GDT_Template.python('ui', 'panel.html', {'field': self})
        return (self.render_title(mode) + " " + self.render_text(mode) + " " + self.render_super_fields(mode)).strip()
