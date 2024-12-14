import re

from gdo.core.GDT_String import GDT_String, Encoding


class GDT_Name(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self._minlen = 2
        self._maxlen = 64
        self._case_s = True
        self.pattern(r'^[a-z][a-z_0-9]+$', re.IGNORECASE)
