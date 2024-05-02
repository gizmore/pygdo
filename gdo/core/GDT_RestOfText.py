from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String


class GDT_RestOfText(GDT_Repeat):

    def __init__(self, name):
        super().__init__(GDT_String(name))

