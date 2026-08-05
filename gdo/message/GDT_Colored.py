from gdo.base.Render import Mode, Render
from gdo.message.GDT_Span import GDT_Span


class GDT_Colored(GDT_Span):
    """An inline span whose colour is rendered only by capable connectors."""

    def __init__(self, color: str):
        super().__init__()
        if color not in ('green', 'red'):
            raise ValueError(f'Unsupported text colour: {color}')
        self._color = color

    def _render_html(self):
        return f'<span class="{self._color}">{super().render_fields(Mode.render_html)}</span>'

    def render_cli(self):
        return getattr(Render, self._color)(super().render_fields(Mode.render_cli), Mode.render_cli)

    def render_irc(self):
        return getattr(Render, self._color)(super().render_fields(Mode.render_irc), Mode.render_irc)
