from gdo.ui.GDT_Span import GDT_Span


class GDT_Italic(GDT_Span):

    def render_txt(self) -> str:
        return self._html
    