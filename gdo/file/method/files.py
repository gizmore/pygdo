from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_File import GDO_File
from gdo.table.MethodQueryTable import MethodQueryTable


class files(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_File.table()

    def gdo_table_headers(self) -> list[GDT]:
        t = self.gdo_table()
        return t.columns_only('file_id', 'file_name')
