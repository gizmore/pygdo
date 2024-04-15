from gdo.core.GDT_Char import GDT_Char


class GDT_Token(GDT_Char):
    TOKEN_LEN = 16

    def __init__(self, name):
        super().__init__(name)
        self._minlen = self.TOKEN_LEN
        self._maxlen = self.TOKEN_LEN
