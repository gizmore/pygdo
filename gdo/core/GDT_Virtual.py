from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.WithName import WithName
from gdo.core.WithProxy import WithProxy


class GDT_Virtual(WithProxy, WithName, GDT):

    def __init__(self, gdt: GDT):
        super().__init__()
        self.name(gdt.get_name())

    def gdo_before_select(self, gdo: GDO, query: Query):
        pass
