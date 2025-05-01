from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.base.GDO import GDO

from enum import Enum
from mysql.connector import ProgrammingError, DataError, DatabaseError, InterfaceError

from gdo.base.Application import Application
from gdo.base.Exceptions import GDODBException, GDOException
from gdo.base.GDT import GDT
from gdo.base.Result import Result

class Type(Enum):
    UNKNOWN = 1
    RAW = 2
    OPTION = 3
    SELECT = 4
    UPDATE = 5
    INSERT = 6
    REPLACE = 7
    DELETE = 8


class Query:
#    MUTEX = threading.Lock()

    _debug: bool
    _raw: str
    _table: str
    _gdo: 'GDO'
    _fetch_as: 'GDO'
    _type: Type
    _columns: str
    _vals: dict[str, str]
    _where: str
    _order: str
    _offset: int
    _limit: int
    _join: str
    _joined_objects: list[str]
    _nocache: bool

    def __init__(self):
        super().__init__()
        self._debug = False
        self._type = Type.UNKNOWN
        self._join = ''
        self._joined_objects = []
        self._where = ''
        self._nocache = False

    def is_select(self):
        if self.is_raw() and self._raw.startswith('SELECT'):
            return True
        return self.is_type(Type.SELECT)

    def is_raw(self):
        return self.is_type(Type.RAW)

    def is_update(self):
        return self.is_type(Type.UPDATE)

    def is_delete(self):
        return self.is_type(Type.DELETE)

    def is_insert(self):
        return self.is_type(Type.INSERT)

    def is_replace(self):
        return self.is_type(Type.REPLACE)

    def is_type(self, _type):
        return self._type == _type

    def type(self, type_: Type):
        self._type = type_
        return self

    def raw(self, query: str):
        self._raw = query
        self._type = Type.RAW
        return self

    def debug(self, debug=True):
        self._debug = debug
        return self

    def table(self, table: str):
        # if hasattr(self, '_table'):
        #     self._table += ','
        #     self._table += table
        # else:
        self._table = table
        return self

    def gdo(self, gdo):
        self._gdo = gdo
        self._fetch_as = gdo
        return self  # .table(gdo.gdo_table_name())

    def fetch_as(self, gdo: 'GDO'):
        self._fetch_as = gdo
        return self

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

    def all(self):
        self._where = '1'
        return self

    def or_where(self, where: str):
        return self.where(where, 'OR')

    def where(self, where: str, op='AND'):
        if self._where:
            self._where += f" {op} ({where})"
        else:
            self._where = f"({where})"
        return self

    def order(self, order: str):
        if hasattr(self, '_order'):
            self._order += f", {order}"
        else:
            self._order = order
        return self

    def no_order(self):
        delattr(self, '_order')
        return self

    def first(self):
        return self.take(1)

    def limit(self, limit: int, offset: int = 0):
        self._limit = limit
        return self.offset(offset)

    def take(self, count: int):
        self._limit = count
        return self

    def offset(self, offset: int):
        self._offset = offset
        return self

    def set_val(self, key: str, val: str):
        return self.set_vals({key: val})

    def set_vals(self, vals: dict):
        if not hasattr(self, '_vals'):
            self._vals = vals
        else:
            self._vals.update(vals)
        return self

    def nocache(self, nocache: bool=True):
        self._nocache = nocache
        return self

    def join_object(self, key: str, join: str = 'JOIN'):
        from gdo.core.GDT_Join import GDT_Join
        from gdo.core.WithObject import WithObject
        if key in self._joined_objects:
            return self
        self._joined_objects.append(key)

        gdt = self._gdo.column(key)

        if isinstance(gdt, GDT_Join):
            join = gdt._join
        elif isinstance(gdt, WithObject):
            table = gdt._table
            a_tbl = self._gdo.gdo_table_name()
            f_tbl = f"{key}_t"
            join = f"{join} {table.gdo_table_name()} AS {f_tbl} ON {f_tbl}.{table.primary_key_column().get_name()}={a_tbl}.{gdt.get_name()}"
        else:
            raise GDODBException(f"Cannot join object {key}", self.build_query())
        return self.join(join)

    def join(self, join: str):
        if hasattr(self, '_join') and self.join is not None:
            self._join += f" {join}"
        else:
            self._join = f" {join}"
        return self

    def build_query(self):
        if self.is_raw():
            return self._raw
        if self.is_select():
            return f"SELECT {self._columns} FROM {self._table} {self._join}{self._build_where()}{self._build_order()}{self.build_limit()}"
        if self.is_delete():
            return f"DELETE FROM {self._table} {self._join} WHERE {self._where}"
        if self.is_insert():
            keys = ",".join(map(lambda v: GDT.escape(v), self._vals.keys()))
            values = ",".join(map(lambda v: GDT.quote(v), self._vals.values()))
            return f"INSERT INTO {self._table} ({keys}) VALUES ({values})"
        if self.is_replace():
            keys = ",".join(map(lambda v: GDT.escape(v), self._vals.keys()))
            values = ",".join(map(lambda v: GDT.quote(v), self._vals.values()))
            return f"REPLACE INTO {self._table} ({keys}) VALUES ({values})"
        if self.is_update():
            set_string = ",".join(map(lambda kv: f"{kv[0]}={GDT.quote(kv[1])}", self._vals.items()))
            return f"UPDATE {self._table} SET {set_string} WHERE {self._where}"
        raise GDOException("err_query_type_unknown")

    def _build_where(self) -> str:
        if self._where:
            return f' WHERE {self._where}'
        return ''

    def _build_order(self):
        if hasattr(self, '_order'):
            return f" ORDER BY {self._order}"
        return ''

    def build_limit(self):
        if not hasattr(self, '_limit'):
            return ''
        if not hasattr(self, '_offset'):
            return f' LIMIT {self._limit}'
        return f' LIMIT {self._offset}, {self._limit}'

    def exec(self, use_dict: bool = True) -> Result:
        db = Application.db()
        db.get_link()
        query = self.build_query()
        try:
            if self.is_select():
                return db.select(query, use_dict, self._fetch_as, self._debug).nocache(self._nocache)
            else:
                return db.query(query, self._debug)
        except (AttributeError, InterfaceError, ProgrammingError, DataError, DatabaseError) as ex:
            raise GDODBException(str(ex), query)
