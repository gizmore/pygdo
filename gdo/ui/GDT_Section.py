from gdo.ui.GDT_Divider import GDT_Divider


class GDT_Section(GDT_Divider):

    def __init__(self, name: str):
        super().__init__()
        self.vert()

    def render_toml(self) -> str:
        return f"\n# {self.render_title()}\n"
