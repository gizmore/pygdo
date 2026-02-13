from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.WithName import WithName
from gdo.core.WithHTMLAttributes import WithHTMLAttributes
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Link(WithHTMLAttributes, WithHREF, WithTitle, WithText, WithName, GDT):

    def __init__(self, name: str=None):
        super().__init__()
        self._name = name # self.generate_name()

    def render_form(self):
        return self.render_html()

    def render_html(self) -> str:
        return f'<a class=gdt-link href="{self.render_href()}"><span>{self.render_text()}</span></a>'

    def render_txt(self) -> str:
        return self.render_text(Mode.render_txt)

    def render_text(self, mode: Mode = Mode.render_html) -> str:
        if self.has_text():
            return super().render_text(mode)
        return self.render_href()