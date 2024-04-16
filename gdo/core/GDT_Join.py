from gdo.base.GDT import GDT


class GDT_Join(GDT):
    _join: str

    def __init__(self):
        super().__init__()

    def join_raw(self, join, type_='LEFT'):
        self._join = f"{type_} JOIN {join}"
        return self

    def join(self, table, as_, on_, type_='LEFT'):
        self._join = f"{type_} JOIN {table.gdo_table_identifier()} AS {as_} ON {on_}"
        return self

    def is_searchable(self):
        return True


