from __future__ import annotations

import functools
import hashlib
import traceback
from functools import lru_cache
from typing import Self, Generator

from gdo.base.Exceptions import GDOException
from gdo.base.Result import ResultType

from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Query import Type, Query
from gdo.base.Trans import t
from gdo.base.Util import Strings, Arrays
from gdo.base.WithBulk import WithBulk
from gdo.base.WithName import WithName


class GDO(WithName, WithBulk, GDT):
    """
    A GDO (Gizmore Data Object) is just a GDT(Gizmore Data Type) with fields that are GDT.
    There is one GDO acting as the table instance, and other entitites are rows.
    """
    ID_SEPARATOR = ':'  # Multiple primary keys supported
    HASH_LENGTH = 16

    #PYPP#START#
    GDO_COUNT = 0
    GDO_ALIVE = 0
    GDO_MAX = 0
    #PYPP#END#

    _vals: dict[str, str|bytes]
    _values: dict[str, any]
    _dirty: list[str]
    _last_id: int|None
    _my_id: str|None

    __slots__ = (
        '_vals',
        '_values',
        '_dirty',
        '_last_id',
        '_my_id',
    )

    def __init__(self):
        super().__init__()
        #PYPP#START#
        GDO.GDO_COUNT += 1
        GDO.GDO_ALIVE += 1
        GDO.GDO_MAX = max(GDO.GDO_MAX, GDO.GDO_ALIVE)
        from gdo.base.Application import Application
        if Application.config('core.gdo_debug') == '2':
            from gdo.base.Logger import Logger
            Logger.debug(str(self.__class__) + "".join(traceback.format_stack()))
        #PYPP#END#
        self._vals = {}
        self._values = {}
        self._dirty = []
        self._last_id = None
        self._my_id = None

    #PYPP#START#
    def __del__(self):
        GDO.GDO_ALIVE -= 1
    #PYPP#END#

    def __str__(self):
        return f"{self.get_name()}({self.get_id()}): {str(list(self._vals.values()))}"

    def __repr__(self):
        return f"{self.get_name()}({self.get_id()}): {str(list(self._vals.values()))}"

    def gdo_redis_fields(self) -> list[str]:
        return [
            '_my_id',
            '_vals',
        ]

    def gdo_wake_up(self) -> Self:
        self._values = {}
        self._dirty = []
        return self

    @classmethod
    def table(cls) -> Self:
        return Cache.table_for(cls)

    @classmethod
    def blank(cls, vals: dict = None) -> Self:
        vals = vals or {}
        for name, gdt in cls.table().columns().items():
            vals[name] = vals.get(name, gdt.get_initial())
        back = cls()
        back._vals = vals
        return back.all_dirty()

    def gdo_hash(self) -> str:
        hash_me = hashlib.sha256()
        for gdt in self.columns().values():
            val = gdt.get_val()
            hash_me.update(val.encode() if val is not None else b'')
        return hash_me.hexdigest()[0:self.HASH_LENGTH]

    def render_name(self):
        return self.get_name()

    def render_list(self):
        return self.render_name()

    @functools.cache
    def primary_key_column(self) -> GDT:
        for gdt in self.columns().values():
            return gdt

    def is_persisted(self) -> bool:
        id_ = self.get_id()
        return len(id_) > 0 and id_ != '0' and not id_.startswith(self.ID_SEPARATOR)

    @classmethod
    @functools.cache
    def gdo_table_name(cls) -> str:
        return cls.__name__.lower()

    def gdo_table_engine(self) -> str:
        return 'InnoDB'

    def gdo_cached(self) -> bool:
        return True

    def gdo_persistent(self) -> bool:
        """
        Mark this table as not being un-cached.
        """
        return False

    ###########
    # Columns #
    ###########

    def gdo_columns(self) -> list[GDT]:
        """
        Return the columns for your GDO right with this method
        """
        raise GDOException(f"{self.__class__.__name__} does not provide any columns in gdo_columns().")

    def column(self, key: str) -> GDT|None:
        # try:
        return Cache.column_for(self.__class__, key).gdo(self)
        # except Exception as ex:
        #     Logger.exception(ex, f"Unknown column {key} in {self.__class__.__name__}")

    def columns(self) -> dict[str,GDT]:
        return Cache.columns_for(self.__class__)

    def columns_only(self, *names: str) -> list[GDT]:
        cols = []
        for key in names:
            cols.append(self.column(key))
        return cols

    @functools.cache
    def column_by_type(self, klass: type[GDT]) -> 'GDT':
        for gdt in self.columns().values():
            if type(gdt) is klass:
                return gdt
        raise GDOException(f"{self.get_name()} has no GDT of type {klass}")

    def gdo_val(self, key: str) -> str:
        return self._vals.get(key)

    def gdo_value(self, key: str) -> any:
        if (v := self._values.get(key)) is not None:
            Cache.VHITS += 1  #PYPP#DELETE#
            return v
        self._values[key] = v = self.column(key).get_value()
        return v

    def set_val(self, key, val: str, dirty: bool = True) -> Self:
        if key in self._values:
            del self._values[key]
        self._vals[key] = val if type(val) is bytes else Strings.nullstr(val)
        return self.dirty(key, dirty)

    def set_value(self, key: str, value: any, dirty: bool=True) -> Self:
        val = self.column(key).to_val(value)
        self._values[key] = value
        self._vals[key] = val if type(val) is bytes else Strings.nullstr(val)
        return self.dirty(key, dirty)

    def set_vals(self, vals: dict[str,str], dirty: bool=True) -> Self:
        for key, val in vals.items():
            self.set_val(key, val, dirty)
        return self

    def save_vals(self, vals: dict) -> Self:
        return self.set_vals(vals).save()

    def save_val(self, key: str, val: str) -> Self:
        self.set_val(key, val)
        return self.save()

    def increment(self, key: str, by: float|int) -> Self:
        return self.save_val(key, str(self.gdo_value(key) + by))

    @classmethod
    def get_name(cls):
        return cls.__name__

    def dirty(self, key: str, dirty: bool = True) -> Self:
        if dirty:
            self._dirty.append(key)
        # if key in self._dirty:
        #     if not dirty:
        #         self._dirty.remove(key)
        # elif dirty:
        #     self._dirty.append(key)
        return self

    def all_dirty(self, dirty: bool=True) -> Self:
        self._dirty = list(self.columns().keys()) if dirty else []
        return self

    def query(self) -> Query:
        return Query().table(self.gdo_table_name()).gdo(self)

    def select(self, columns: str='*') -> Query:
        query = self.query().select(columns)
        self.before_select(query)
        return query

    def count_where(self, where: str='1') -> int:
        col = self.select('COUNT(*)').where(where).exec(False).iter(ResultType.ROW).fetch_val()
        return 0 if col is None else int(col)

    def get_pk_columns(self) -> Generator[GDT]:
        yield from [gdt.gdo(self) for gdt in Cache.pk_columns_for(self.__class__)]

    def get_by(self, key: str, val: str) -> Self:
        return self.get_by_vals({key: val})

    def get_by_aid(self, id_: str) -> Self:
        """
        Get a row by auto inc id.
        """
        if c := Cache.obj_search_gid(self, id_): return c
        return (self.table().select().where(f"{self.primary_key_column().get_name()}={self.quote(id_)}").
                first().exec().fetch_object())

    def get_by_id(self, *id_: str):
        if self.gdo_cached():
            if c := Cache.obj_search_gid(self, self.ID_SEPARATOR.join(id_)): return c
        return self.table().select().where(' AND '.join(
            [f'{gdt.get_name()}={self.quote(id_[i])}'
             for i, gdt in enumerate(self.get_pk_columns())])
        ).first().exec().fetch_object()

    def pk_where(self) -> str:
        cols = list(self.get_pk_columns()) # or self.columns()
        return " AND ".join(f"{gdt.get_name()}={GDT.quote(gdt.get_val())}" for gdt in cols)

    def get_by_vals(self, vals: dict[str, str]) -> Self:
        if cached := Cache.obj_search(self, vals):
            return cached
        where = []
        for k, v in vals.items():
            where.append(f'{k}={self.quote(v)}')
        return self.table().select().where(' AND '.join(where)).first().exec().fetch_object()

    def get_id(self) -> str:
        if self._my_id:
            return self._my_id
        pks = list(self.get_pk_columns())
        if len(pks) == 0:
            pks = self.columns().values()
        elif len(pks) == 1:
            return pks[0].get_val() or ''
        v = pks[0].get_val()
        if v.startswith('0') or v.startswith(':'):
            return ''
        self._my_id = self.ID_SEPARATOR.join(gdt.get_val() or '' for gdt in pks)
        return self._my_id

    def get_ids(self) -> list[str]:
        return [gdt.get_val() for gdt in self.get_pk_columns()]

    ############
    # Validate #
    ############
    def validated(self):
        for name, gdt in self.columns().items():
            if not gdt.gdo(self).validated():
                raise GDOException(t('err_gdo_validate', (name, gdt.render_error())))
        return self

    ####################
    # Insert / Replace #
    ####################

    def soft_replace(self) -> Self:
        if old := self.get_by_id(*self.get_ids()):
            old.set_vals(self._vals).save()
            old._values = {}
            return old.all_dirty(False)
        return self.all_dirty().insert()

    def insert(self) -> Self:
        return self.insert_or_replace(Type.INSERT)

    def replace(self) -> Self:
        return self.insert_or_replace(Type.REPLACE)

    def insert_or_replace(self, type_: Type) -> Self:
        self.before_create()
        query = self.query().type(type_).set_vals(self.insert_vals())
        self._last_id = query.exec().lastrowid
        self.after_create()
        self.all_dirty(False)
        return Cache.update_for(self)

    def dirty_vals(self) -> dict[str, str]:
        vals = {}
        for name, gdt in self.columns().items():
            if hasattr(gdt, '_val'):
                if name in self._dirty and not gdt.is_primary():
                    vals.update(gdt.gdo(self).dirty_vals())
        return vals

    def insert_vals(self) -> dict[str, str]:
        vals = {}
        for gdt in self.columns().values():
            if hasattr(gdt, '_val'):
                vals.update(gdt.gdo(self).dirty_vals())
        return vals

    def save(self):
        if not self.is_persisted():
            return self.insert()
        obj = self
        if len(self._dirty):
            dirty = self.dirty_vals()
            obj.before_update()
            obj.query().type(Type.UPDATE).set_vals(dirty).where(self.pk_where()).exec()
            obj.after_update()
            from gdo.base.IPC import IPC
            if Arrays.mem_size(dirty) > IPC.MAX_EVENT_ARG_SIZE:
                dirty = None
            obj.all_dirty(False)
            if obj.gdo_cached():
                IPC.send('base.ipc_gdo', (self.gdo_table_name(), self.get_id(), dirty))
                return Cache.update_for(obj)
        return obj

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
            if self.gdo_cached():
                Cache.obj_search_id(self, vals, True)
            self.after_delete()
            self.all_dirty(True)
        return self

    def delete_where(self, where: str, with_hooks: bool = False) -> int:
        """
        Runs a delete query and executes it and returns nothing.... this is quite a todo.
        """
        return self.delete_query().where(where).exec().rowcount

    def delete_by_vals(self, vals: dict, with_hooks: bool = False):
        query = self.delete_query()
        for key, val in vals.items():
            query.where(f"{key}={self.quote(val)}")
        query.exec()
        Cache.obj_search_pygdo(self, vals, True)
        Cache.obj_search_redis(self, vals, True)

    def delete_by_id(self, *ids: str):
        if gdo := self.get_by_id(*ids):
            gdo.delete()
            return gdo

    ##########
    # Reload #
    ##########
    def reload(self):
        self._vals = self.select().where(self.pk_where()).exec().fetch_assoc()
        self._values = {}
        self._dirty = []
        self.on_reload()
        return self

    ##########
    # Events #
    ##########
    def on_reload(self):
        Cache.reload(self.gdo_table_name(), self.get_id())
        return self

    def before_select(self, query: Query):
        for gdt in self.columns().values():
            gdt.gdo_before_select(self, query)
        self.gdo_before_select(self, query)

    def before_create(self):
        for gdt in self.columns().values():
            gdt.gdo_before_create(self)
        self.gdo_before_create(self)

    def after_create(self):
        for gdt in self.columns().values():
            gdt.gdo_after_create(self)
        self.gdo_after_create(self)

    def before_update(self):
        for gdt in self.columns().values():
            gdt.gdo_before_update(self)
        self.gdo_before_update(self)

    def after_update(self):
        self.gdo_after_update(self)
        for gdt in self.columns().values():
            gdt.gdo_after_update(self)

    def before_delete(self):
        for gdt in self.columns().values():
            gdt.gdo_before_delete(self)
        self.gdo_before_delete(self)

    def after_delete(self):
        self.gdo_after_delete(self)
        for gdt in self.columns().values():
            gdt.gdo_after_delete(self)

    #######
    # All #
    #######

    def all(self, where: str = '1', result_type: ResultType = ResultType.OBJECT) -> list['Self']:
        return self.table().select().where(where).exec().iter(result_type).fetch_all()

    def all_cached(self, where: str = '1', result_type: ResultType = ResultType.OBJECT) -> list['Self']:
        cache_key = f"{self.gdo_table_name()}_all_{where}_{result_type}"
        if cached := Cache.get(cache_key, where):
            return cached
        cached = self.all(where, result_type)
        Cache.set(cache_key, where, cached)
        return cached

    ########
    # Name #
    ########
    def name_column(self) -> GDT:
        from gdo.core.GDT_Name import GDT_Name
        return self.column_of(GDT_Name)

    def column_of(self, type: type[GDT]) -> GDT|None:
        for gdt in self.columns().values():
            if isinstance(gdt, type):
                return gdt.gdo(self)
