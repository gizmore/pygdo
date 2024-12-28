from gdo.core.GDT_Enum import GDT_Enum
from gdo.message.Editor import Editor


class GDT_Editor(GDT_Enum):

    EDITORS = {}

    def __init__(self, name: str):
        super().__init__(name)

    @classmethod
    def register(cls, editor: type[Editor]):
        cls.EDITORS[editor.__class__.__name__.lower()] = editor

    def gdo_choices(self) -> dict:
        return self.__class__.EDITORS
