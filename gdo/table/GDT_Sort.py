from gdo.core.GDT_Int import GDT_Int


class GDT_Sort(GDT_Int):

    def __init__(self, name: str):
        super().__init__(name)
        self.bytes(2)

