from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Italic(GDT_Span):

    def render(self, mode: Mode = Mode.HTML) -> str:
        return Render.italic(super().render(mode), mode)
