from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Stroke(GDT_Span):

    def get_tag(self) -> str:
        return 'strike'

    def render_cli(self):
        return Render.strike(super().render_fields(Mode.render_cli), Mode.render_cli)

    def render_markdown(self):
        return Render.strike(super().render_fields(Mode.render_markdown), Mode.render_markdown)

    def render_irc(self):
        return Render.strike(super().render_fields(Mode.render_irc), Mode.render_irc)

    def render_telegram(self):
        return Render.strike(super().render_fields(Mode.render_telegram), Mode.render_telegram)
