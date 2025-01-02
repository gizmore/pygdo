from gdo.base.Render import Render, Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Bold(GDT_Span):

    def get_tag(self) -> str:
        return 'b'
