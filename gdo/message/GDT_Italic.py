from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Italic(GDT_Span):

    def get_tag(self) -> str:
        return 'i'

    def render_markdown(self):
        return f"*{super().render_fields(Mode.MARKDOWN)}*"

    def render_cli(self):
        return Render.italic(super().render_fields(Mode.CLI), Mode.CLI)
