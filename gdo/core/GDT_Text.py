from gdo.core.GDT_String import GDT_String


class GDT_Text(GDT_String):
    """
    A longer chunk of text, using a different mysql column define
    """

    def __init__(self, name):
        super().__init__(name)

    def gdo_column_define(self) -> str:
        return (f"{self._name} TEXT({self._maxlen}) "
                f"CHARSET {self.gdo_column_define_charset()} COLLATE {self.gdo_column_define_collate()} "
                f"{self.gdo_column_define_default()} "
                f"{self.gdo_column_define_null()} ")

