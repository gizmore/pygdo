from gdo.table.GDT_Table import TableMode
from gdo.table.MethodQueryTable import MethodQueryTable


class MethodQueryList(MethodQueryTable):
    """A query-backed table method rendered as a simple list."""

    def gdo_table_mode(self) -> TableMode:
        return TableMode.LIST
