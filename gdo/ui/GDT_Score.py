from gdo.core.GDT_Int import GDT_Int


class GDT_Score(GDT_Int):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('trophy')
        self.bytes(4)
        self.not_null()
        self.initial('0')
