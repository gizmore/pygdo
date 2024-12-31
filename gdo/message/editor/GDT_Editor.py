from gdo.core.GDT_Enum import GDT_Enum
from gdo.message.editor.Editor import Editor


class GDT_Editor(GDT_Enum):

    EDITORS = {}

    def __init__(self, name: str):
        super().__init__(name)
        self.initial('html')

    @classmethod
    def register(cls, editor: type[Editor]):
        cls.EDITORS[editor.get_name()] = editor

    def gdo_choices(self) -> dict:
        return self.EDITORS
