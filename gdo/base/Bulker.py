from gdo.base.GDO import GDO
from gdo.base.GDT import GDT


class Bulker:
    """
    Bulk insertion manager that flushes on the limit.
    """

    _chunk_size: int
    _gdo: GDO
    _columns: list[GDT]
    _column_names: list[str]
    _rows: list[list[str]]
    _replace: bool

    def __init__(self, gdo: GDO, columns: list[GDT], replace: bool, chunk_size: int) -> None:
        self._gdo = gdo
        self._columns = columns
        self._column_names = []
        self._chunk_size = chunk_size
        self._rows = []
        self._replace = replace
        for gdt in columns:
            self._column_names.append(gdt.get_name())

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def add(self, row: list[str]) -> None:
        self._rows.append(row)
        if len(self._rows) >= self._chunk_size:
            self.flush()

    def flush(self):
        if self._rows:
            if self._replace:
               self._gdo.bulk_replace(self._columns, self._rows, len(self._rows))
            else:
                self._gdo.bulk_insert(self._columns, self._rows, len(self._rows))
            self._rows.clear()

    def addIfNotExist(self, data: list[str]) -> None:
        vals = {}
        for i, cname in enumerate(self._column_names):
            vals[cname] = data[i]
        if not self._gdo.get_by_vals(vals):
            self.add(data)
