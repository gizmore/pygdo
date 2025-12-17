from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Render import Render
from gdo.ui.WithFlow import WithFlow
from gdo.ui.WithTitle import WithTitle


class GDT_Divider(WithTitle, WithFlow, GDT):
    """
    A flow aware horizontal or vertical divider. Little gray line.
    """

    DIV_CLI_CHAR = '='
    MAX_CLI_WIDTH = 96

    def __init__(self):
        super().__init__()
        self._flow_horz = True

    def render_html(self) -> str:
        return '\n<span class="gdt-divider gdt-horizontal"></span>\n'

    def render_form(self) -> str:
        return f'<div class="gdt-divider {self.render_class()}">{self.render_title()}</div>\n'

    def render_txt(self):
        return self.render_cli()

    def render_cli(self):
        title = self.render_title(Mode.render_cli)
        cli = Mode.render_cli
        if self.is_horizontal():
            if title:
                title = Render.underline(Render.bold(title, cli), cli)
                return f" | {title}: "
            else:
                return " | "
        width = len(title)
        side = self.DIV_CLI_CHAR * int((self.MAX_CLI_WIDTH - width - 2) / 2)
        return f"{side}_{title}_{side}"
