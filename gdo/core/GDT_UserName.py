import regex

from gdo.core.GDT_String import GDT_String


class GDT_UserName(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.minlen(1)
        self.maxlen(32)
        self.pattern(r'^[\p{L}\p{N}][\p{L}\p{N}_\-.]{0,31}$', regex.IGNORECASE)

