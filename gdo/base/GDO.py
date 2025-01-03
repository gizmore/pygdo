from __future__ import annotations

import hashlib
import traceback

from gdo.base.Exceptions import GDOException
from gdo.base.Logger import Logger
from gdo.base.Result import ResultType

from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Query import Type, Query
from gdo.base.Util import Strings
from gdo.base.WithBulk import WithBulk


class GDO(WithBulk, GDT):
    """
    A GDO (Gizmore Data Object) is just a GDT(Gizmore Data Type) with s are GDT
    """
    ID_SEPARATOR = ':'  # Multiple primary keys supported
    GDO_COUNT = 0
    GDO_ALIVE = 0
    GDO_MAX = 0

    _vals: dict[str, str]
    _dirty: list[str]
    _last_id: int|None

    __slots__ = (
        '_vals',
        '_dirty',
        '_last_id',
    )

    def __init__(self):
        super().__init__()
        GDO.GDO_COUNT += 1
        GDO.GDO_ALIVE += 1
        GDO.GDO_MAX = max(GDO.GDO_MAX, GDO.GDO_ALIVE)
        from gdo.base.Application import Application
        if Application.config('core.gdo_debug') == '2':
            from gdo.base.Logger import Logger
            Logger.debug(str(self.__class__) + "".join(traceback.format_stack()))
        self._vals = {}
        self._dirty = []
        self._last_id = None

    def __del__(self):
        GDO.GDO_ALIVE -= 1

    @classmethod
    def table(cls) -> 'GDO':
        return Cache.table_for(cls)

    @classmethod
    def blank(cls, vals: dict = None):
        vals = {} if vals is None else vals
        gdo = cls.table()
        for gdt in gdo.columns():
            name = gdt.get_name()
            vals[name] = vals[name] if name in vals.keys() else gdt.get_initial()
        back = cls()
        back._vals.update(vals)
        back.all_dirty()
        return back

    def gdo_hash(self) -> str:
        hash_me = hashlib.sha256()
        for gdt in self.columns():
            val = gdt.get_val()
            hash_me.update(val.encode('utf-8') if val is not None else b'')
        return hash_me.hexdigest()[0:24]

    def render_name(self):
        return self.get_name()

    def primary_key_column(self):
        return self.columns()[0]

    def is_persisted(self):
        id_ = self.get_id()
        return len(id_) > 0 and not id_.startswith(':')

    def gdo_table_name(self) -> str:
        return self.__class__.__name__.lower()

    def gdo_engine_fast(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        """
        Return the columns for your GDO right with this method
        """
        return []

    def column(self, key: str) -> GDT | any:
        """

        :rtype: object
        """
        if gdt := Cache.column_for(self.__class__, key):
            return gdt.gdo(self)
        else:
            raise GDOException(f"Unknown column name {key} for {self.__class__.__name__}")

    def columns(self) -> list[GDT]:
        return Cache.columns_for(self.__class__)

    def columns_only(self, *names: str):
        cols = []
        for key in names:
            cols.append(self.column(key))
        return cols

    def column_by_type(self, klass: type) -> 'GDT':
        for gdt in self.columns():
            if isinstance(gdt, klass):
                return gdt
        raise GDOException(f"{self.get_name()} has no GDT of type {klass}")

    def gdo_val(self, key):
        if key not in self._vals:
            return None
        return self._vals[key]

    def gdo_value(self, key: str):
        return self.column(key).get_value()

    def set_val(self, key, val: str, dirty: bool = True):
        # if key in self._vals.keys():
        #     if val == self._vals[key]:
        #         dirty = False
        if isinstance(val, bytearray):
            val = val.decode()
        if self._vals[key] == val:
            dirty = False
        self._vals[key] = Strings.nullstr(val)
        return self.dirty(key, dirty)

    def set_value(self, key, value, dirty=True):
        val = self.column(key).value(value).to_val(value)
        return self.set_val(key, val, dirty)

    def set_vals(self, vals: dict, dirty=True):
        for key, val in vals.items():
            self.set_val(key, val, dirty)
        return self

    def save_vals(self, vals: dict):
        self.set_vals(vals)
        return self.save()

    def save_val(self, key: str, val: str):
        self.set_val(key, val)
        return self.save()

    def increment(self, key: str, by: float|int):
        old = self.gdo_value(key)
        return self.set_val(key, str(old + by))

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

    def query(self) -> Query:
        return Query().table(self.gdo_table_name()).gdo(self)

    def select(self, columns='*') -> Query:
        return self.query().select(columns)

    def count_where(self, where='1') -> int:
        col = self.select('COUNT(*)').where(where).exec(False).iter(ResultType.ROW).fetch_val()
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

    def get_by_id(self, *id_: str):
        cols = self.get_pk_columns()
        return self.get_by_vals({
            col.get_name(): Strings.nullstr(val) for col, val in zip(cols, id_) if val})

    def pk_where(self) -> str:
        cols = self.get_pk_columns()
        return " AND ".join(map(lambda gdt: f"{gdt.get_name()}={GDT.quote(gdt._val)}", cols))

    def get_by_vals(self, vals: dict[str, str]):
        cached = Cache.obj_search(self, vals)
        if cached:
            return cached
        where = []
        for k, v in vals.items():
            where.append(f'{k}={self.quote(v)}')
        return self.table().select().where(' AND '.join(where)).first().exec().fetch_object()

    def get_id(self) -> str:
        cols = self.get_pk_columns()
        return self.ID_SEPARATOR.join(map(lambda gdt: gdt._val or '', cols))

    ####################
    # Insert / Replace #
    ####################

    def soft_replace(self):
        old = self.get_by_id(*self.get_id().split(':'))
        if old is not None:
            return self.save()
        return self.insert()

    def insert(self):
        return self.insert_or_replace(Type.INSERT)

    def replace(self):
        return self.insert_or_replace(Type.REPLACE)

    def insert_or_replace(self, type_: Type):
        self.before_create()
        query = self.query().type(type_).set_vals(self.insert_vals())
        self._last_id = query.exec()
        self.after_create()
        return self.all_dirty(False)

    def dirty_vals(self) -> dict:
        from gdo.core.GDT_Field import GDT_Field
        vals = {}
        for gdt in self.columns():
            if isinstance(gdt, GDT_Field):
                name = gdt.get_name()
                if name in self._dirty:
                    vals[name] = self.gdo_val(name)
        return vals

    def insert_vals(self):
        from gdo.core.GDT_Field import GDT_Field
        vals = {}
        for gdt in self.columns():
            if isinstance(gdt, GDT_Field):
                name = gdt.get_name()
                vals[name] = self.gdo_val(name)
        return vals

    def save(self):
        if not self.is_persisted():
            return self.insert()
        if len(self._dirty):
            self.before_update()
            query = self.query().type(Type.UPDATE).set_vals(self.dirty_vals()).where(self.pk_where())
            query.exec()
            self.after_update()
            return self.all_dirty(False)
        else:
            return self

    ##########
    # Delete #
    ##########

    def delete_query(self):
        return self.query().type(Type.DELETE)

    def delete(self):
        if self.is_persisted():
            self.before_delete()
            self.delete_query().where(self.pk_where()).exec()
            vals = {gdt.get_name(): gdt.get_val() for gdt in self.get_pk_columns()}
            Cache.obj_search(self.table(), vals, True)
            self.after_delete()
            self.all_dirty(True)
        return self

    def delete_where(self, where: str, with_hooks: bool = False):
        """
        Runs a delete query and executes it and returns nothing.... this is quite a todo.
        """
        self.delete_query().where(where).exec()

    def delete_by_vals(self, vals: dict, with_hooks: bool = False):
        query = self.delete_query()
        for key, val in vals.items():
            query.where(f"{key}={self.quote(val)}")
        Cache.obj_search(self.table(), vals, True)
        query.exec()

    ##########
    # Events #
    ##########

    def before_create(self):
        for gdt in self.columns():
            gdt.gdo_before_create(self)
        self.gdo_before_create(self)

    def after_create(self):
        for gdt in self.columns():
            gdt.gdo_after_create(self)
        self.gdo_after_create(self)

    def before_update(self):
        for gdt in self.columns():
            gdt.gdo_before_update(self)
        self.gdo_before_update(self)

    def after_update(self):
        Cache.obj_for(self).set_vals(self._vals, False)  # After a blanked update this is required.
        self.gdo_after_update(self)
        for gdt in self.columns():
            gdt.gdo_after_update(self)

    def before_delete(self):
        for gdt in self.columns():
            gdt.gdo_before_delete(self)
        self.gdo_before_delete(self)

    def after_delete(self):
        self.gdo_after_delete(self)
        for gdt in self.columns():
            gdt.gdo_after_delete(self)

    #######
    # All #
    #######

    def all(self, where: str = '1', result_type: ResultType = ResultType.OBJECT) -> list['GDO']:
        return self.table().select().where(where).exec().iter(result_type).fetch_all()

    ########
    # Name #
    ########
    def name_column(self) -> GDT:
        from gdo.core.GDT_Name import GDT_Name
        return self.column_of(GDT_Name)

    def column_of(self, type) -> GDT:
        for gdt in self.columns():
            if isinstance(gdt, type):
                return gdt



