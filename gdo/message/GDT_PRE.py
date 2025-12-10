from gdo.base.Render import Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_PRE(GDT_Span):

    def get_tag(self) -> str:
        return 'pre'

    def render_markdown(self):
        return "\n\n" + super().render_fields(Mode.render_markdown) + "\n\n"
