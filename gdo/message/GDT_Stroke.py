from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Stroke(GDT_Span):

    def render(self, mode: Mode = Mode.HTML) -> str:
        return Render.strike(super().render(mode), mode)
