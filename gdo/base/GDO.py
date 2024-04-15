from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import Self

from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Query import Type, Query
from gdo.base.Util import Strings, Arrays
from gdo.base.WithBulk import WithBulk


class GDO(WithBulk, GDT):

    COUNT = 0
    MAX_COUNT = 0

    _vals: dict
    _dirty: list
    _is_table: bool

    def __init__(self):
        super().__init__()
        self.COUNT += 1
        self.MAX_COUNT = max(self.MAX_COUNT, self.COUNT)
        self._vals = {}
        self._dirty = []
        self._is_table = False

    @classmethod
    def table(cls) -> Self:
        return Cache.table_for(cls)

    @classmethod
    def blank(cls, vals: dict):
        gdo = cls.table()
        for gdt in gdo.columns():
            name = gdt.get_name()
            if name:
                gdt._val = vals[name] if name in vals.keys() else ''
        back = cls().set_vals(vals)
        return back

    def primary_key_column(self):
        return self.columns()[0]

    def is_persisted(self):
        return len(self._dirty) == 0

    def gdo_columns(self) -> list[GDT]:
        return []

    def column(self, key: str) -> GDT:
        return Cache.column_for(self.__class__, key).gdo(self)

    def columns(self) -> list[GDT]:
        return Cache.columns_for(self.__class__)

    def gdo_val(self, key):
        if key not in self._vals.keys():
            return None
        return self._vals[key]

    def gdo_value(self, key: str):
        return self.column(key).get_value()

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
        from gdo.base.Query import Query
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

    def get_by(self, key: str, val: str):
        return self.get_by_vals({key: val})

    def get_by_id(self, id: str):
        cols = self.get_pk_columns()
        ids = id.split(':')
        return self.get_by_vals({col.get_name(): Strings.nullstr(val) for col, val in zip(cols, ids) if val})

    def pk_where(self) -> str:
        cols = self.get_pk_columns()
        return " AND ".join(map(lambda gdt: f"{gdt.get_name()}={GDT.quote(gdt._val)}", cols))

    def get_by_vals(self, vals: dict[str, str]):
        where = []
        for k, v in vals.items():
            where.append(f'{k}={self.quote(v)}')
        return self.select().where(' AND '.join(where)).first().exec().fetch_object()

    def get_id(self) -> str:
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
        self.before_create()
        query = self.query().type(type).set_vals(self._vals)
        query.exec()
        self.after_create()
        return self.all_dirty(False)

    def delete(self):
        return self

    def dirty_vals(self):
        vals = {}
        for gdt in self.columns():
            vals[gdt.get_name()] = self.gdo_val(gdt.get_name())
        return vals

    def save(self):
        if len(self._dirty):
            self.before_update()
            query = self.query().type(Type.UPDATE).set_vals(self.dirty_vals()).where(self.pk_where())
            query.exec()
            self.after_update()
            return self.all_dirty(False)
        else:
            return self

    ##########
    # Events #
    ##########

    def before_create(self):
        for gdt in self.columns():
            gdt.gdo_before_create(self)
        self.gdo_before_create(self)
        pass

    def after_create(self):
        for gdt in self.columns():
            gdt.gdo_after_create(self)
        self.gdo_after_create(self)

    def before_update(self):
        for gdt in self.columns():
            gdt.gdo_before_update(self)
        self.gdo_before_update(self)

    def after_update(self):
        for gdt in self.columns():
            gdt.gdo_after_update(self)
        self.gdo_after_update(self)




