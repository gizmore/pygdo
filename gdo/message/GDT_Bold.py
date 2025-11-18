from gdo.base.Render import Render, Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_Bold(GDT_Span):

    def get_tag(self) -> str:
        return 'b'

    def render_markdown(self):
        return f"**{super().render_fields(Mode.render_markdown)}**"

    def render_cli(self):
        return Render.bold(super().render_fields(Mode.render_cli), Mode.render_cli)
