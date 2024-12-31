from gdo.base.GDO import GDO
from gdo.base.Result import Result
from gdo.base.ResultArray import ResultArray
from gdo.core.GDO_File import GDO_File
from gdo.table.MethodTable import MethodTable


class dir_server(MethodTable):

    def gdo_table(self) -> GDO:
        return GDO_File.table()

    def gdo_table_result(self) -> Result:
        # TODO populate the list with all files in directory
        return ResultArray([], self.gdo_table())

    def gdo_trigger(self) -> str:
        return ''

