from gdo.base.Render import Render, Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Bold(GDT_Span):

    def render(self, mode: Mode = Mode.HTML) -> str:
        return Render.bold(super().render(mode), mode)
