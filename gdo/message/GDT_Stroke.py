from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Stroke(GDT_Span):

    def get_tag(self) -> str:
        return 'strike'
