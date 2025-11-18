from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.message.WithHTMLAttributes import WithHTMLAttributes


class GDT_Span(WithHTMLAttributes, GDT_Container):

    def get_tag(self) -> str:
        return 'span'

    def render(self, mode: Mode = Mode.html):
        if mode == Mode.html:
            tag = self.get_tag()
            attrs = self.html_attrs()
            attrs = f" {attrs}" if attrs else ''
            return f"<{tag}{attrs}>{super().render(mode)}</{tag}>"
        return self.render_gdt(mode)
