from gdo.core.GDT_Float import GDT_Float


class GDT_Decimal(GDT_Float):
    _digits_before: int
    _digits_after: int

    def __init__(self, name: str):
        super().__init__(name)
        self._digits_before = 11
        self._digits_after = 3

    def digits(self, before: int, after: int):
        self._digits_before = before
        self._digits_after = after
        return self

    def gdo_column_define(self) -> str:
        before = self._digits_before + self._digits_after
        return f"{self.get_name()} DECIMAL({before},{self._digits_after}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"
