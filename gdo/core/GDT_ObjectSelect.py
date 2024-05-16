from gdo.core.GDT_Select import GDT_Select
from gdo.core.WithObject import WithObject


class GDT_ObjectSelect(WithObject, GDT_Select):

    def gdo_choices(self) -> dict:
        return self._table.select().exec().fetch_all_dict()
