from gdo.base.Query import Query
from gdo.core.GDT_String import GDT_String


class GDT_Search(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('search')

    def search_query(self, query: Query) -> Query:
        if not (term := self.get_val()):
            return query
        table = self._gdo
        for gdt in table.columns().values():
            gdt.gdo_search_query(query, term)
        return query.apply_search_wheres()
