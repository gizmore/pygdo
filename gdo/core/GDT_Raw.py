from gdo.core.GDT_String import GDT_String


class GDT_Raw(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)

    def render_txt(self) -> str:
        return self.get_val()

    def render_html(self) -> str:
        return self.get_val()
