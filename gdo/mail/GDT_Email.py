from gdo.core.GDT_String import GDT_String


class GDT_Email(GDT_String):

    def __init__(self, name):
        super().__init__(name)
        self.pattern("^[^@\\s]+@[^@\\s]+$")
        self.icon('email')
