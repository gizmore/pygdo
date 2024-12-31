from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.message.GDT_HTML import GDT_HTML
from gdo.message.WithHTMLAttributes import WithHTMLAttributes


class GDT_Span(WithHTMLAttributes, GDT_Container):

    def get_tag(self) -> str:
        return 'span'

    def render(self, mode: Mode = Mode.HTML):
        if mode == Mode.HTML:
            tag = self.get_tag()
            return f"<{tag}>{super().render(mode)}</{tag}>"
        return super().render(mode)
