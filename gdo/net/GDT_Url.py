from gdo.core.GDT_String import GDT_String


class GDT_Url(GDT_String):

    _schemes: [str]

    def __init__(self, name):
        super().__init__(name)
        self._schemes = ['http', 'https']

    def schemes(self, schemes):
        self._schemes = schemes

    def validate(self, value):
        if not super().validate(value):
            return False
        return True
