from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Stroke(GDT_Span):

    def get_tag(self) -> str:
        return 'strike'

    def render_cli(self):
        return Render.strike(super().render_fields(Mode.CLI), Mode.CLI)
