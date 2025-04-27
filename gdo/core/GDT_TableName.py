from gdo.base.GDO_GDOTable import GDO_GDOTable
from gdo.core.GDT_Object import GDT_Object


class GDT_TableName(GDT_Object):

    def __init__(self, name: str):
        super().__init__(name)
        self.table(GDO_GDOTable.table())
