import regex

from gdo.core.GDT_String import GDT_String


class GDT_UserName(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.minlen(1)
        self.maxlen(32)
        self.gen_pattern()

    def minlen(self, minlen: int):
        self._min_len = minlen
        return self.gen_pattern()

    def maxlen(self, maxlen: int):
        self._max_len = maxlen
        return self.gen_pattern()

    def gen_pattern(self):
        return self.pattern(r'^[\p{L}\p{N}][\p{L}\p{N}_\-.]{'+str(self._min_len-1)+','+str(self._max_len-1)+'}$', regex.IGNORECASE if not self._case_s else 0)
