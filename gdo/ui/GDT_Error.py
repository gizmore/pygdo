from gdo.base.Render import Render, Mode
from gdo.base.Trans import t
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Error(GDT_Panel):

    def __init__(self):
        super().__init__()

    def render_cli(self):
        return Render.red(f"{t('error')}: {self.render_title(Mode.CLI)}: {self.render_text(Mode.CLI)}", Mode.CLI)
