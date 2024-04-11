from enum import Enum

from mysql.connector.cursor import MySQLCursorDict


class IterType(Enum):
    ROW = 1
    ASSOC = 2
    OBJECT = 3


class Result:
    _result: MySQLCursorDict
    _table: object
    _iter = IterType.OBJECT

    def __init__(self, result, gdo):
        self._result = result
        self._table = gdo

    def type(self, iter_type: IterType):
        self._iter = iter_type
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self._iter == IterType.ROW:
            data = self.fetch_row()
        elif self._iter == IterType.ASSOC:
            data = self.fetch_assoc()
        else:
            data = self.fetch_object()
        if data is None:
            raise StopIteration
        return data

    def fetch_row(self):
        row = self._result.fetchone()
        if row is None:
            return None
        return list(row.values())

    def fetch_assoc(self):
        row = self._result.fetchone()
        if row is None:
            return None
        return row

    def fetch_val(self):
        row = self.fetch_row()
        if row is None:
            return None
        return row[0]

    def fetch_object(self):
        row = self.fetch_assoc()
        if row is None:
            return None
        obj = self._table.__class__()
        obj.set_vals(row)
        return obj
