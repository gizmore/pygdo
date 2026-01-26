from gdo.core.GDT_String import GDT_String
import regex


class GDT_Name(GDT_String):
    def _init__(self, name):
        super().__init__(name)
        self.ascii()
        self._min_len = 2
        self._max_len = 64
        self._case_s = True
        self.pattern(r'^[a-zA-Z][-\.A-Za-z_0-9]+$', regex.IGNORECASE)
        