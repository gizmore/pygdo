from gdo.base.Render import Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Paragraph(GDT_Span):

    def render(self, mode: Mode = Mode.HTML):
        if mode == Mode.HTML:
            return f"<p>{super().render(mode)}</p>"
        return super().render(mode)
