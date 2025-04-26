from typing import Self

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.WithName import WithName
from gdo.core.WithProxy import WithProxy


class GDT_Virtual(WithProxy, WithName, GDT):

    _query: Query|None

    def __init__(self, gdt: GDT):
        super().__init__()
        self.name(gdt.get_name())
        self._query = None

    def query(self, query: Query) -> Self:
        self._query = query
        return self

    def gdo_before_select(self, gdo: GDO, query: Query):
        query.select(f"( {self._query.build_query()} ) AS {self.get_name()}")
        pass
