from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Underline(GDT_Span):
    """Underline text for renderers which can express it."""

    def get_tag(self) -> str:
        return 'u'

    def render_cli(self):
        return Render.underline(super().render_fields(Mode.render_cli), Mode.render_cli)

    def render_irc(self):
        return Render.underline(super().render_fields(Mode.render_irc), Mode.render_irc)

    def render_telegram(self):
        return Render.underline(super().render_fields(Mode.render_telegram), Mode.render_telegram)

