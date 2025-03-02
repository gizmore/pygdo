from gdo.core.GDT_String import GDT_String


class GDT_Email(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)
        self.ascii().maxlen(96).case_i()
        self.pattern("^[^@\\s]+@[^@\\s]+$")
        self.icon('email')
