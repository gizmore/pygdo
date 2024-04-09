from enum import Enum

from gdo.core.Application import Application
from gdo.core.Logger import Logger
from gdo.db.Result import Result


class Type(Enum):
    UNKNOWN = 1
    RAW = 2
    OPTION = 3
    SELECT = 4
    UPDATE = 5
    INSERT = 6
    DELETE = 7


class Query:
    _debug: bool
    _raw: str
    _table: str
    _gdo: object
    _type: Type
    _columns: str
    _where: str
    _offset: int
    _limit: int

    def __init__(self):
        super().__init__()
        self._debug = False
        self._type = Type.UNKNOWN

    def is_select(self):
        return self.is_type(Type.SELECT)

    def is_raw(self):
        return self.is_type(Type.RAW)

    def is_update(self):
        return self.is_type(Type.UPDATE)

    def is_type(self, _type):
        return self._type == _type

    def raw(self, query: str):
        self._raw = query
        return self

    def debug(self, debug=True):
        self._debug = debug
        return self

    def table(self, table: str):
        if hasattr(self, '_table'):
            self._table += ','
            self._table += table
        else:
            self._table = table
        return self

    def gdo(self, gdo):
        self._gdo = gdo
        return self.table(gdo.gdo_table_name())

    def select(self, columns='*'):
        self._type = Type.SELECT
        if hasattr(self, '_columns'):
            self._columns += ','
            self._columns += columns
        else:
            self._columns = columns
        return self

    def only_select(self, columns: str):
        delattr(self, '_columns')
        return self.select(columns)

    def where(self, where, op='AND'):
        if hasattr(self, '_where'):
            self._where += f" {op} {where}"
        else:
            self._where = where
        return self

    def first(self):
        return self.take(1)

    def limit(self, limit: int, offset: int):
        self._limit = limit
        return self.offset(offset)

    def take(self, count):
        self._limit = count
        return self

    def offset(self, offset):
        self._offset = offset
        return self

    def build_query(self):
        if self.is_raw():
            return self._raw
        if self.is_select():
            return (
                f"SELECT {self._columns} FROM {self._table} WHERE {self._where} {self.buildLimit()}"
            )

    def buildLimit(self):
        if not hasattr(self, '_limit'):
            return ''
        if not hasattr(self, '_offset'):
            return f'LIMIT {self._limit}'
        return f'LIMIT {self._limit, self._offset}'

    def exec(self):
        query = self.build_query()
        if self._debug:
            Logger.debug(query)
        result = Application.DB.query(query)
        if self.is_select():
            return Result(result, self._gdo)
        return True

