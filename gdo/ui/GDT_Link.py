from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Link(WithHREF, WithTitle, WithText, GDT_String):
    """A string field rendered as a link, including normal table features."""

    def __init__(self, name: str=None):
        super().__init__(name)
        self.label(name or 'link')
        self.icon('link')

    def render_form(self):
        return self.render_html()

    def render_html(self) -> str:
        return f'<a class="gdt-link" href="{self.render_href()}"{self.html_attrs()}><span>{self.render_icon(Mode.render_html)}{self.render_text()}</span></a>'

    def render_cell(self) -> str:
        return self.render_html()

    def render_card(self) -> str:
        return self.render_html()

    def render_txt(self) -> str:
        return self.render_text(Mode.render_txt)

    def render_text(self, mode: Mode = Mode.render_html) -> str:
        if self.has_text():
            return super().render_text(mode)
        return self.render_href()
