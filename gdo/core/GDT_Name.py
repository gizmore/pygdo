import regex

from gdo.core.GDT_String import GDT_String


class GDT_Name(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self._min_len = 2
        self._maxlen = 64
        self._case_s = True
        self.pattern(r'^[a-zA-Z][A-Za-z_0-9]+$', regex.IGNORECASE)
