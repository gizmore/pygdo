from gdo.core.GDT_String import GDT_String


class GDT_Char(GDT_String):

    def __init__(self, name):
        super().__init__(name)

    def maxlen(self, maxlen: int):
        super().maxlen(maxlen)
        return self.minlen(maxlen)
