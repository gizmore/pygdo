import functools
from enum import Enum

from mysql.connector.cursor import MySQLCursorDict
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from gdo.base.GDO import GDO
    from gdo.core.GDT_Dict import GDT_Dict
    from gdo.core.GDT_List import GDT_List

from gdo.base.Cache import Cache


class ResultType(Enum):
    ROW = 1
    ASSOC = 2
    OBJECT = 3


class Result:
    _result: MySQLCursorDict
    _table: 'GDO'
    _iter: ResultType
    _nocache: bool

    def __init__(self, result: MySQLCursorDict, gdo: 'GDO' = None):
        self._result = result
        self._table = gdo
        if gdo is None:
            pass
        self._iter = ResultType.OBJECT
        self._nocache = False

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

    def nocache(self, nocache: bool=True):
        self._nocache = nocache
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

    GDT_Dict = None
    def gdt_dict(self):
        if self.__class__.GDT_Dict is None:
            from gdo.core.GDT_Dict import GDT_Dict
            self.__class__.GDT_Dict = GDT_Dict
        return self.__class__.GDT_Dict

    GDT_List = None
    def gdt_list(self):
        if self.__class__.GDT_List is None:
            from gdo.core.GDT_List import GDT_List
            self.__class__.GDT_List = GDT_List
        return self.__class__.GDT_List


    def fetch_all(self) -> 'GDT_List':
        return self.gdt_list()(*[row for row in self])

    def fetch_all_dict(self) -> 'GDT_Dict':
        result = self.gdt_dict()()
        mode = self._iter
        setitem = result.__setitem__
        if mode is ResultType.OBJECT:
            for row in self:
                setitem(row.get_id(), row)
        elif mode is ResultType.ASSOC:
            for row in self:
                setitem(next(iter(row)), row)
        else:
            for row in self:
                setitem(row[0], row)
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
        return row

    def fetch_val(self, col_num: int = 0):
        """
        Fetch the first column of the next row.
        """
        row = self.fetch_row()
        return None if row is None else row[col_num]

    @functools.cache
    def get_reused_object(self) -> 'GDO':
        return self._table.__class__()

    def fetch_object(self) -> 'GDO':
        """
        Fetch the next row as an object piped through the cache
        """
        if (row := self.fetch_assoc()) is None:
            return None
        if self._nocache:
            obj = self._table.gdo_real_class(row)()
            obj._vals = row
            obj._blank = False
            return obj
        else:
            obj = self._table.gdo_real_class(row)()
            obj._vals = row
            obj._blank = False
            return Cache.obj_for(obj, None, False)

    def fetch_column(self, col_num: int = 0) -> list[str]:
        result = []
        while row := self.fetch_row():
            result.append(row[col_num])
        return result
