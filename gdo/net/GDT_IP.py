from gdo.core.GDT_String import GDT_String


class GDT_IP(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.minlen(3)
        self.maxlen(39)
        self.ascii()
        self._pattern = '/^[0-9.:]*$/'


