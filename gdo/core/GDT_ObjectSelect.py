from gdo.base import GDO
from gdo.base.Query import Query
from gdo.core.GDT_Select import GDT_Select
from gdo.core.WithObject import WithObject


class GDT_ObjectSelect(WithObject, GDT_Select):
    
    def __init__(self, name: str):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return self.gdo_query().exec().fetch_all_dict()

    def gdo_query(self) -> Query:
        return self._table.select()
