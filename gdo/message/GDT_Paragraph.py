from gdo.base.Render import Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Paragraph(GDT_Span):

    def get_tag(self) -> str:
        return 'p'
