from gdo.core.GDT_Int import GDT_Int


class GDT_UInt(GDT_Int):

    def __init__(self, name: str):
        super().__init__(name)
        self._signed = False
        self._min = 0
        self.icon('numeric')
