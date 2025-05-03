from gdo.base.Render import Mode
from gdo.base.WithName import WithName
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_TemplateHTML import tplhtml
from gdo.ui.WithFlow import WithFlow


class GDT_Bar(WithFlow, WithName, GDT_Container):

    def __init__(self, name: str = None):
        super().__init__()
        self.name(name or self.generate_name())

    def render_html(self, mode: Mode = Mode.HTML):
        return tplhtml('ui', 'bar.html', {
            'name': self.get_name(),
            'class': self.render_class(),
            'fields': self.render_bar_fields(),
        })

    def render_bar_fields(self):
        return "\n".join([f"<li>{gdt.render_html()}</li>" for gdt in self.fields()])
