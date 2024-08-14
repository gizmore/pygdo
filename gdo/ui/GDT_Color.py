from gdo.core.GDT_String import GDT_String


class GDT_Color(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.minlen(3)
        self.maxlen(32)
