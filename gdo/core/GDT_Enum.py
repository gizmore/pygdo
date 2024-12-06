from gdo.core.GDT_Select import GDT_Select


class GDT_Enum(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return self._choices

    def gdo_column_define(self) -> str:
        values = "','".join(key for key in self.init_choices())
        return f"{self._name} ENUM ('{values}') CHARSET ascii COLLATE ascii_bin {self.gdo_column_define_null()}{self.gdo_column_define_default()}"
