import sys

from gdo.core.GDT_Field import GDT_Field


class GDT_Int(GDT_Field):
    _min: int
    _max: int
    _bytes: int
    _signed: bool

    def __init__(self, name: str):
        super().__init__(name)
        self._signed = True
        self._bytes = 4
        self._min = -sys.maxsize - 1
        self._max = sys.maxsize

    def bytes(self, _bytes: int):
        self._bytes = _bytes
        return self

    def signed(self, signed: bool):
        self._signed = signed
        return self

    def unsigned(self, unsigned=True):
        self._signed = not unsigned
        return self

    def gdo_column_define_size(self):
        match self._bytes:
            case 1:
                return 'TINY'
            case 2:
                return 'MEDIUM'
            case 8:
                return 'BIG'
            case _:
                return ''

    def gdo_column_define_sign(self):
        if not self._signed:
            return 'UNSIGNED'
        return ''

    def gdo_column_define(self) -> str:
        return (f"{self._name} {self.gdo_column_define_size()}INT {self.gdo_column_define_sign()}"
                f" {self.gdo_column_define_null()} {self.gdo_column_define_default()}")

    def validate(self, value):
        if not super().validate(value):
            return False
        return self.validate_min_max(value)

    def validate_min_max(self, value):
        return True
    

