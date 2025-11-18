from gdo.base.Render import Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Anchor(GDT_Span):

    def get_tag(self) -> str:
        return 'a'

    def render_markdown(self):
        return f"[{super().render_fields(Mode.markdown)}]({self.attr('href')})"
