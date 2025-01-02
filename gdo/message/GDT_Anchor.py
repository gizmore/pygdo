from gdo.message.GDT_Span import GDT_Span


class GDT_Anchor(GDT_Span):

    def get_tag(self) -> str:
        return 'a'
