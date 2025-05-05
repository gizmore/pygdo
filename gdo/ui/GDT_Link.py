from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Util import Strings
from gdo.base.WithName import WithName
from gdo.core.GDT_Template import GDT_Template
from gdo.core.GDT_TemplateHTML import GDT_TemplateHTML, tplhtml
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Link(WithHREF, WithTitle, WithText, WithName, GDT):

    def __init__(self):
        super().__init__()
        self._name = self.generate_name()

    def render_form(self):
        return self.render_html()

    def render_html(self) -> str:
        return f'<a class=gdt-link href="{self.render_href()}"><span>{self.render_text()}</span></a>'

    def render_txt(self) -> str:
        return self.render_text(Mode.TXT)

    def render_text(self, mode: Mode = Mode.HTML) -> str:
        if self.has_text():
            return super().render_text(mode)
        return self.render_href()