from gdo.core.GDT_Select import GDT_Select


class GDT_Bool(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        choices = {}
        if not self._not_null:
            choices['2'] = 'please_select'
        choices['1'] = 'yes'
        choices['0'] = 'no'
        return choices
