from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_Object import GDT_Object


class GDT_File(GDT_Object):

    def __init__(self, name: str):
        super().__init__(name)
        self.table(GDO_File.table())
