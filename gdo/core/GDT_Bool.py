from gdo.core.GDT_Select import GDT_Select
from gdo.core.GDT_UInt import GDT_UInt


class GDT_Bool(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_column_define(self) -> str:
        return GDT_UInt(self.get_name()).bytes(1).gdo_column_define()

    def gdo_choices(self) -> dict:
        choices = {}
        if not self._not_null:
            choices[''] = 'please_select'
        choices['1'] = 'yes'
        choices['0'] = 'no'
        return choices

    def to_value(self, val: str):
        if val == '1':
            return True
        elif val == '0':
            return False
        else:
            return None
