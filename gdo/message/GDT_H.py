from gdo.base.Render import Mode
from gdo.message.GDT_Span import GDT_Span


class GDT_H(GDT_Span):

    _level: int

    def __init__(self):
        super().__init__()
        self._level = 1

    def get_tag(self) -> str:
        return f"h{self._level}"

    def render_markdown(self):
        h = "#" * self._level
        return f"{h} {super().render_fields(Mode.MARKDOWN)}"

    def render_cli(self):
        return super().render_fields(Mode.CLI)
