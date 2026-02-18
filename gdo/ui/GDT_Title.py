from gdo.core.GDT_String import GDT_String


class GDT_Title(GDT_String):

    _level: int

    def __init__(self, name: str):
        super().__init__(name)
        self._level = 3
        self.label('title')
        self.maxlen(96)

    def level(self, level: int):
        self._level = level
        return self

    def render_html(self) -> str:
        return f"<h{self._level}>{super().render_html()}</h{self._level}>"

    def render_markdown(self):
        return ("#" * self._level) + self.render_txt()