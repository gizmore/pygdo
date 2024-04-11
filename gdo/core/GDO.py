from __future__ import annotations
from typing import TYPE_CHECKING

from gdo.core.Util import Strings
from gdo.core.Query import Type

if TYPE_CHECKING:
    from _typeshed import Self
from gdo.core.Cache import Cache
from gdo.core.GDT import GDT


class GDO(GDT):
    _vals: dict
    _dirty: list
    _is_table: bool

    def __init__(self):
        super().__init__()
        self._vals = {}
        self._dirty = []
        self._is_table = False

    @classmethod
    def table(cls) -> Self:
        return Cache.table_for(cls)

    @classmethod
    def blank(cls, vals: dict):
        return 1

    def gdo_primary_key_column(self):
        return self.columns()[0]

    def gdo_columns(self):
        return []

    def columns(self) -> list[GDT]:
        return Cache.columns_for(self.table().__class__)

    def get(self, key):
        if not key in self._vals.keys():
            return None
        return self._vals[key]

    def set(self, key, val, dirty=True):
        if key in self._vals.keys():
            if val == self._vals[key]:
                dirty = False
        if isinstance(val, bytearray):
            val = val.decode()
        self._vals[key] = str(val)
        return self.dirty(key, dirty)

    def set_vals(self, vals: dict, dirty=True):
        for key, val in vals.items():
            self.set(key, val, dirty)
        return self

    def gdo_table_name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls):
        return cls.__name__

    def dirty(self, key, dirty=True):
        if key in self._dirty:
            if not dirty:
                self._dirty.remove(key)
        else:
            if dirty:
                self._dirty.append(key)
        return self

    def all_dirty(self, dirty=True):
        if dirty:
            self._dirty = list(map(lambda gdt: gdt.get_name(), self.columns()))
        else:
            self._dirty = []
        return self

    def query(self):
        from gdo.core.Query import Query
        return Query().gdo(self)

    def select(self, columns='*'):
        return self.query().select(columns)

    def count_where(self, where='1'):
        col = self.select('COUNT(*)').where(where).exec().fetch_val()
        if col is None:
            return 0
        return int(col)

    def get_pk_columns(self) -> list[GDT]:
        cols = []
        for gdt in self.columns():
            if gdt.is_primary():
                cols.append(gdt.gdo(self))
        return cols

    def get_by_id(self, id: str):
        cols = self.get_pk_columns()
        data = {}
        ids = id.split(':')
        i = 0
        for col in cols:
            if ids[i] == '':
                return None
            data[col.get_name()] = Strings.nullstr(ids[i])
            i += 1
        return self.get_by_vars(data)

    def get_by_vars(self, vals: dict[str, str]):
        where = []
        for k, v in vals.items():
            where.append(f'{k}={self.quote(v)}')
        return self.select().where(','.join(where)).first().exec().fetch_object()

    def get_id(self):
        cols = self.get_pk_columns()
        return ':'.join(map(lambda gdt: gdt._val, cols))

    def soft_replace(self):
        old = self.get_by_id(self.get_id())
        if old is not None:
            return self.save()
        return self.insert()

    def insert(self):
        return self.insertOrReplace(Type.INSERT)

    def replace(self):
        return self.insertOrReplace(Type.REPLACE)

    def insertOrReplace(self, type: Type):
        query = self.query().type(type).set_vals(self.dirty_vals())
        query.exec()
        return self.all_dirty(False)

    def delete(self):
        return self

    def dirty_vals(self):
        vals = {}
        for gdt in self.columns():
            vals[gdt.get_name()] = self.get(gdt.get_name())
        return vals

    def save(self):
        query = self.query().type(Type.UPDATE).set_vals(self.dirty_vals())
        query.exec()
        return self.all_dirty(False)
