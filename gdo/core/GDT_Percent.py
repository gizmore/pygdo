from gdo.core.GDT_Float import GDT_Float


class GDT_Percent(GDT_Float):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('percent')
        self.label('percent')
