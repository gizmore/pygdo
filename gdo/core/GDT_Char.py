from gdo.core.GDT_String import GDT_String


class GDT_Char(GDT_String):

    def __init__(self, name):
        super().__init__(name)

    def maxlen(self, maxlen: int):
        super().maxlen(maxlen)
        super().minlen(maxlen)
        return self

    def minlen(self, minlen: int):
        super().maxlen(minlen)
        super().minlen(minlen)
        return self

    def gdo_varchar_define(self) -> str:
        return 'CHAR'
