import traceback
from enum import Enum
from mysql.connector import ProgrammingError, DataError, DatabaseError

from gdo.base.Application import Application
from gdo.base.Exceptions import GDODBException
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
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
    _debug: bool
    _raw: str
    _table: str
    _gdo: object
    _type: Type
    _columns: str
    _vals: dict[str, str]
    _where: str
    _order: str
    _offset: int
    _limit: int
    _join: str
    _joined_objects: list[str]

    def __init__(self):
        super().__init__()
        self._debug = False
        self._type = Type.UNKNOWN
        self._join = ''
        self._joined_objects = []

    def is_select(self):
        if self.is_raw() and self._raw.startswith('SELECT'):
            return True
        return self.is_type(Type.SELECT)

    def is_raw(self):
        return self.is_type(Type.RAW)

    def is_update(self):
        return self.is_type(Type.UPDATE)

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

    def all(self):
        self._where = '1'
        return self

    def or_where(self, where: str):
        return self.where(where, 'OR')

    def where(self, where: str, op='AND'):
        if hasattr(self, '_where'):
            self._where += f" {op} ({where})"
        else:
            self._where = f"({where})"
        return self

    def order(self, order: str):
        if hasattr(self, '_order'):
            self._order += f" {order}"
        else:
            self._order = order
        return self

    def no_order(self):
        delattr(self, '_order')
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

    def set_val(self, key: str, val: str):
        return self.set_vals({key: val})

    def set_vals(self, vals: dict):
        if not hasattr(self, '_vals'):
            self._vals = {}
        self._vals.update(vals)
        return self

    def join_object(self, key: str, join: str = 'JOIN'):
        from gdo.core.GDT_Join import GDT_Join
        from gdo.core.GDT_Object import GDT_Object
        if key in self._joined_objects:
            return self
        self._joined_objects.append(key)

        gdt = self._gdo.column(key)

        if isinstance(gdt, GDT_Join):
            join = gdt._join
        elif isinstance(gdt, GDT_Object):
            table = gdt._table
            a_tbl = self._gdo.gdo_table_name()
            f_tbl = f"{key}_t"
            join = f"{join} {table.gdo_table_name()} AS {f_tbl} ON {f_tbl}.{table.primary_key_column().get_name()}={a_tbl}.{gdt.get_name()}"
        else:
            raise GDODBException("Cannot join object", self.build_query())
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
        if self.is_select():
            return (
                f"SELECT {self._columns} FROM {self._table} {self._join} WHERE {self._where}{self._build_order()} {self.buildLimit()}"
            )

    def _build_order(self):
        if hasattr(self, '_order'):
            return f" ORDER BY {self._order}"
        return ''

    def buildLimit(self):
        if not hasattr(self, '_limit'):
            return ''
        if not hasattr(self, '_offset'):
            return f'LIMIT {self._limit}'
        return f'LIMIT {self._limit, self._offset}'

    def exec(self, use_dict: bool = True):
        Application.DB.get_link()
        if Application.config('db.debug') in ('1', '2'):
            self.debug()
        query = self.build_query()
        try:
            if self._debug:
                Logger.debug("#" + str(Application.STORAGE.db_queries + 1) + ": " + query)
                if Application.config('db.debug') == '2':
                    Logger.debug("".join(traceback.format_stack()))
            if self.is_insert():
                cursor = Application.DB.cursor()
                Application.STORAGE.db_writes += 1
                Application.STORAGE.db_queries += 1
                cursor.execute(query)
                return cursor.lastrowid
            if self.is_select():
                cursor = Application.DB.cursor(use_dict)
                Application.STORAGE.db_reads += 1
                Application.STORAGE.db_queries += 1
                cursor.execute(query)
                return Result(cursor, self._gdo)
            if self.is_update():
                return Application.DB.query(query)
            else:
                return Application.DB.query(query)
        except AttributeError as ex:
            raise GDODBException(str(ex), query)
        except ProgrammingError as ex:
            raise GDODBException(ex.msg, query)
        except DataError as ex:
            raise GDODBException(ex.msg, query)
        except DatabaseError as ex:
            raise GDODBException(ex.msg, query)
