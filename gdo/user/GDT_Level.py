from gdo.core.GDT_UInt import GDT_UInt


class GDT_Level(GDT_UInt):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('score')

