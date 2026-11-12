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
        self._proxy = gdt
        self._query = None
        self._auto_select = False

    def query(self, query: Query) -> Self:
        self._query = query
        return self

    def auto_select(self, enabled: bool = True) -> Self:
        """Include this virtual column in every ordinary GDO select."""
        self._auto_select = enabled
        return self

    def select_into(self, query: Query) -> Query:
        """Explicitly add the virtual expression to a select query."""
        if self._query is None:
            raise ValueError(f'Virtual column {self.get_name()} has no query')
        return query.select(f"( {self._query.build_query()} ) AS {self.get_name()}")

    def gdo_before_select(self, gdo: GDO, query: Query):
        if self._auto_select:
            self.select_into(query)
