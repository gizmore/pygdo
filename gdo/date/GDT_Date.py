from gdo.date.GDT_Timestamp import GDT_Timestamp


class GDT_Date(GDT_Timestamp):

    def __init__(self, name):
        super().__init__(name)
        self._input_type = 'date'

    def gdo_column_define(self) -> str:
        return f"{self._name} DATE {self.gdo_column_define_null()}{self.gdo_column_define_default()}"
