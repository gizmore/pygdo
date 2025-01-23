from gdo.base.Render import Mode
from gdo.base.WithName import WithName
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import tpl, GDT_Template
from gdo.ui.WithFlow import WithFlow


class GDT_Bar(WithFlow, WithName, GDT_Container):

    def __init__(self, name: str = None):
        super().__init__()
        self.name(name or self.generate_name())

    def render(self, mode: Mode = Mode.HTML):
        if mode.is_html():
            return GDT_Template.python('ui', 'bar.html', {'field': self})
        return super().render_fields(mode)
