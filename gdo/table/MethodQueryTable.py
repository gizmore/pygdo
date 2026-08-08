from gdo.base.Query import Query
from gdo.base.Result import Result
from gdo.table.MethodTable import MethodTable



class MethodQueryTable(MethodTable):

    def gdo_table_query(self) -> Query:
        return self.gdo_table().select()

    def get_num_results(self) -> int:
        query = self.gdo_table_query()
        self.apply_table_filters(query)
        return int(query.only_select('COUNT(*)').no_order().exec().fetch_val() or 0)

    def apply_table_filters(self, query: Query):
        if self.gdo_filtered():
            self.table_filter_field().filter_query(query, self)
        return query

    def get_table_result(self) -> Result:
        query = self.apply_table_filters(self.gdo_table_query())
        if self.gdo_ordered():
            self.table_order_field().order_query(query)
        if self.gdo_paginated():
            self.table_paginate_field().paginate_query(query, self.gdo_paginate_size())
        return query.exec()
