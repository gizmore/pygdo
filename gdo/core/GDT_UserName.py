from gdo.core.GDT_String import GDT_String


class GDT_UserName(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.minlen(2)
        self.maxlen(32)
        self.pattern('^[a-z][A-Z][a-z_A-Z0-9]{1,31}$')
