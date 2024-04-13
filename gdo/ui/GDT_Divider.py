from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Render import Render
from gdo.ui.WithFlow import WithFlow
from gdo.ui.WithTitle import WithTitle


class GDT_Divider(WithTitle, WithFlow, GDT):

    DIV_CLI_CHAR = '='
    MAX_CLI_WIDTH = 96

    """
    A flow aware horizontal or vertical divider. Little gray line.
    """

    def __init__(self):
        super().__init__()

    def render_cli(self):
        title = self.render_title()
        cli = Mode.CLI
        title = Render.underline(Render.bold(title, cli), cli)
        if self.is_horizontal():
            return f"|{title}: "
        width = len(title)
        side = self.DIV_CLI_CHAR * int((self.MAX_CLI_WIDTH - width - 2) / 2)
        return f"{side}_{title}_{side}"
