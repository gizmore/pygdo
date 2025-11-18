from gdo.base.Render import Mode
from gdo.ui.GDT_Divider import GDT_Divider


class GDT_Section(GDT_Divider):

    def __init__(self):
        super().__init__()
        self.vertical()

    def render_toml(self) -> str:
        return f"\n# {self.render_title(Mode.toml)}\n"
