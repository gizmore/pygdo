from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.GDT_TemplateHTML import tplhtml
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle



class GDT_Panel(WithTitle, WithText, GDT):

    def __init__(self):
        super().__init__()

    def render(self, mode: Mode = Mode.HTML):
        return self.render_html() if mode.is_html() else f"{self.render_title(mode)} - {self.render_text(mode)}".strip()

    def render_html(self):
        return tplhtml('ui', 'panel.html', {
            'html_class': self.html_class(),
            'title': self.render_title(),
            'text': self.render_text(),
        })
