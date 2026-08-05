import re

from gdo.core.GDT_String import GDT_String


class GDT_Name(GDT_String):
    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self._min_len = 2
        self._max_len = 64
        self.pattern(r'^[a-z0-9][-_a-z0-9]*$', re.IGNORECASE)
