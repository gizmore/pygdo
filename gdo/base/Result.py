from enum import Enum
from mysql.connector.cursor import MySQLCursorDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.base.GDO import GDO

from gdo.base.Cache import Cache


class ResultType(Enum):
    ROW = 1
    ASSOC = 2
    OBJECT = 3


class Result:
    _result: MySQLCursorDict
    _table: 'GDO'
    _iter = ResultType.OBJECT

    def __init__(self, result: MySQLCursorDict, gdo: 'GDO' = None):
        self._result = result
        self._table = gdo

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, '_result'):
            try:
                self._result.close()
            except:
                pass
            delattr(self, '_result')

    def iter(self, iter_type: ResultType):
        self._iter = iter_type
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self._iter == ResultType.ROW:
            data = self.fetch_row()
        elif self._iter == ResultType.ASSOC:
            data = self.fetch_assoc()
        else:
            data = self.fetch_object()
        if data is None:
            self.close()
            raise StopIteration
        return data

    def fetch_all(self) -> list['GDO']:
        return [row for row in self]

    def fetch_all_dict(self) -> dict:
        result = {}
        if self._iter == ResultType.OBJECT:
            for row in self:
                result[row.get_id()] = row
        elif self._iter == ResultType.ASSOC:
            for row in self:
                result[next(iter(row.keys()))] = row
        else:
            for row in self:
                result[row[0]] = row
        return result

    def fetch_row(self) -> list[str] | None:
        row = self._result.fetchone()
        if row is None:
            self.close()
            return None
        if isinstance(row, dict):
            return list(row.values())
        return list(row)

    def fetch_assoc(self):
        row = self._result.fetchone()
        if row is None:
            self.close()
            return None
        return row

    def fetch_val(self):
        """
        Fetch the first column of the next row.
        """
        row = self.fetch_row()
        result = None if row is None else row[0]
        self.close()
        return result

    def fetch_object(self) -> 'GDO':
        """
        Fetch the next row as an object piped through the cache
        """
        row = self.fetch_assoc()
        if row is None:
            return None
        obj = self._table.__class__()
        obj._vals.update(row)
        obj.all_dirty(False)
        return Cache.obj_for(obj)

    def fetch_column(self, col_num: int = 0) -> list[str]:
        result = []
        while row := self.fetch_row():
            result.append(row[col_num])
        return result
