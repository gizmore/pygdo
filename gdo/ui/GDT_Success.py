from gdo.base.Render import Render, Mode
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Success(GDT_Panel):

    def __init__(self):
        super().__init__()

    def render_cli(self):
        return Render.green(self.render_text(Mode.CLI), Mode.CLI)
