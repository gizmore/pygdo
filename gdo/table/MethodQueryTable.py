from gdo.base.Query import Query
from gdo.base.Result import Result
from gdo.table.MethodTable import MethodTable


class MethodQueryTable(MethodTable):

    def gdo_table_query(self) -> Query:
        return self.gdo_table().select()

    def get_table_result(self) -> Result:
        query = self.gdo_table_query()
        self.table_order_field().order_query(query)
        return query.exec()
