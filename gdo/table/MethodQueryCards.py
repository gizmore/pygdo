from gdo.table.GDT_Table import TableMode
from gdo.table.MethodQueryTable import MethodQueryTable


class MethodQueryCards(MethodQueryTable):
    """A query-backed table method rendered as cards in web contexts."""

    def gdo_table_mode(self) -> TableMode:
        return TableMode.CARDS
