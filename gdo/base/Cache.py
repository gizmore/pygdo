import hashlib
import functools
import zlib

import msgpack
from redis import Redis
from functools import lru_cache, wraps

from gdo.base import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Util import Files
from gdo.base.WithSerialization import WithSerialization


class Cache:
    """
    The wonderful pygdo cache in 187 lines of code.
    There are 4 caches:
    1) TCACHE holds GDO.table() objects to re-use GDTs.
    2) CCACHE holds GDO.gdo_columns() GDTs to re-use them.
    3) OCACHE holds GDO entities for single identity cache.
    3) REDIS (FCACHE) is the tad slower process shared memory cache.
    (c) 2025 by gizmore@wechall.net and chappy@chappy-bot.net.
    """
    HITS = 0
    MISS = 0
    UPDATES = 0
    REMOVES = 0

    TCACHE: dict[str, GDO] = {}             # class_name => GDO.table() mapping
    CCACHE: dict[str, list[GDT]] = {}       # class_name => GDO.gdo_columns() mapping
    OCACHE: dict[str, dict[str, GDO]] = {}  # table_name => dict[id, GDO] mapping
    RCACHE: Redis = None                    # key => dict[key, WithSerialization] mapping

    @classmethod
    def init(cls, enabled: bool = False, host: str = 'localhost', port: int = 6379, db: int = 0):
        if enabled:
            cls.RCACHE = Redis(host=host, port=port, db=db, decode_responses=False)

    @classmethod
    def clear(cls):
        cls.TCACHE = {}
        cls.CCACHE = {}
        cls.OCACHE = {}
        if cls.RCACHE:
            cls.RCACHE.flushdb()
        Files.empty_dir(Application.file_path('cache/'))

    @classmethod
    def clear_stats(cls):
        cls.UPDATES = cls.MISS = cls.REMOVES = cls.HITS = 0

    @classmethod
    def clear_ocache(cls):
        """
        Clear request OCACHE for non persistent GDO
        """
        for gdo_klass, gdo in cls.TCACHE.items():
            t = gdo.gdo_table_name()
            if not gdo.gdo_persistent():
                cls.OCACHE[t].clear()

    #############
    # T/C/Cache #
    #############

    @classmethod
    def table_for(cls, gdo_klass: type[GDO]):
        cn = gdo_klass
        if cn not in cls.TCACHE:
            cls.TCACHE[cn] = gdo_klass()
            cls.CCACHE[cn] = cls.build_ccache(gdo_klass)
            cls.OCACHE[gdo_klass.gdo_table_name()] = {}
        return cls.TCACHE[cn]

    @classmethod
    def build_ccache(cls, gdo_klass: type[GDO]):
        cache = []
        columns = cls.TCACHE[gdo_klass].gdo_columns()
        for column in columns:
            cache.append(column)
            cache.extend(column.gdo_components())
        return cache

    @classmethod
    def columns_for(cls, gdo_klass: type[GDO]):
        cls.table_for(gdo_klass)
        return cls.CCACHE[gdo_klass]

    @classmethod
    def column_for(cls, gdo_klass: GDO, key: str) -> GDT:
        for gdt in cls.columns_for(gdo_klass):
            if gdt.get_name() == key:
                return gdt

    ##########
    # OCACHE #
    ##########

    @classmethod
    def obj_for(cls, gdo: GDO, after_write: bool = False, is_rc = False) -> GDO:
        if gdo.gdo_cached():
            gid = gdo.get_id()
            cn = gdo.gdo_table_name()

            ocached = cls.OCACHE[cn].get(gid)
            if ocached:
                ocached._vals.update(gdo._vals)
                return ocached

            rcached = None
            if is_rc:
                rcached = gdo
            elif not after_write:
                rcached = cls.get(cn, gid)
            if ocached:
                if rcached: # Update ocache from redis
                    ocached._vals.update(rcached._vals)
                    gdo = ocached
                else: # No RCACHE. Populate
                    ocached._vals.update(gdo._vals)
                    cls.set(cn, gid, ocached)
                    gdo = ocached
            else:  # No OCACHE. Populate
                if rcached:
                    if is_rc:
                        gdo = gdo.blank().all_dirty(False)
                    cls.OCACHE[cn][gid] = gdo
                    gdo._vals.update(rcached._vals)
                else: # Neither found it
                    cls.OCACHE[cn][gid] = gdo
                    if not after_write:
                        cls.set(cn, gid, gdo)
        return gdo

    @classmethod
    def update_for(cls, gdo: GDO):
        cls.set(gdo.gdo_table_name(), gdo.get_id(), gdo)
        return cls.obj_for(gdo, True)

    @classmethod
    def obj_search_id(cls, gdo: GDO, vals: dict, delete: bool = False):
        tn = gdo.gdo_table_name()
        gid = ":".join(v for v in vals.values())
        if ocached := cls.OCACHE[tn].get(gid):
            if delete:
                del cls.OCACHE[tn][gid]
                cls.remove(tn, gid)
            return ocached
        if rcached := cls.get(tn, gid):
            if delete:
                cls.remove(tn, gid)
                return rcached
            return cls.obj_for(rcached, is_rc=True)

    @classmethod
    def obj_search(cls, gdo: GDO, vals: dict, delete: bool = False):
        return cls.obj_search_pygdo(gdo, vals, delete)

    @classmethod
    def obj_search_pygdo(cls, gdo: GDO, vals: dict, delete: bool = False):
        if gdo.gdo_cached():
            cn = gdo.gdo_table_name()
            for oc in cls.OCACHE[cn].values():
                found = True
                for k, v in vals.items():
                    if oc.gdo_val(k) != v:
                        found = False
                        break
                if found:
                    cls.HITS += 1
                    if delete:
                        gid = oc.get_id()
                        cls.remove(gid)
                        del cls.OCACHE[cn][gid]
                    return oc

    @classmethod
    def obj_search_redis(cls, gdo: GDO, vals: dict, delete: bool = False):
        if gdo.gdo_cached():
            cn = gdo.gdo_table_name()
            cursor = 0
            while True:
                cursor, keys = cls.RCACHE.scan(cursor, match=f"{cn}:*")
                for key in keys:
                    key = key.decode()
                    if rc := cls.get(key):
                        found = True
                        for k, v in vals.items():
                            if rc.gdo_val(k) != v:
                                found = False
                                break
                        if found:
                            cls.HITS += 1
                            if delete:
                                cls.remove(key)
                                id = rc.get_id()
                                if id in cls.OCACHE[cn]:
                                    del cls.OCACHE[cn][id]
                                    return None
                            return cls.obj_for(rc, after_write=True, is_rc=True)
                if cursor == 0:
                    break
            cls.MISS += 1

    ##########
    # FCACHE #
    ##########

    @classmethod
    def get(cls, key: str, args_key: str = None, default: any = None):
        if cls.RCACHE:
            try:
                key = f"{key}:{args_key}" if args_key else key
                if packed := cls.RCACHE.get(key):
                    cls.HITS += 1
                    return WithSerialization.gdounpack(zlib.decompress(packed))
                cls.MISS += 1
            except Exception as ex:
                Logger.exception(ex)
        return default

    @classmethod
    def set(cls, key: str, args_key: str | None, value: WithSerialization):
        if cls.RCACHE:
            if isinstance(value, WithSerialization):
                value = value.gdopack()
            else:
                value = msgpack.dumps(value)
            cls.UPDATES += 1
            key = f"{key}:{args_key}" if args_key else key
            cls.RCACHE.set(key, zlib.compress(value))

    @classmethod
    def remove(cls, key: str = None, args_key: str = None):
        if cls.RCACHE:
            if key is None:
                cls.REMOVES += 1
                cls.RCACHE.flushdb()
            elif args_key is None:
                cursor = 0
                while True:
                    cursor, keys = cls.RCACHE.scan(cursor, match=f"{key}:*")
                    if keys:
                        cls.REMOVES += 1
                        cls.RCACHE.delete(*keys)
                    if cursor == 0:
                        break
            else:
                cls.REMOVES += 1
                redis_key = f"{key}:{args_key}"
                cls.RCACHE.delete(redis_key)



#############
# Decorator #
#############

def _hash_args(args, kwargs):
    # todo sort kwargs by key
    return hashlib.md5(str((args, frozenset(kwargs.items()))).encode()).hexdigest()

def gdo_cached(cache_key: str):
    def decorator(func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_key = _hash_args(args, kwargs)
            if (cached_value := Cache.get(cache_key, args_key)) is not None:
                return cached_value
            result = func(*args, **kwargs)
            Cache.set(cache_key, args_key, result)
            return result
        return wrapper
    return decorator



def gdo_instance_cached():
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            cache_name = f"_{method.__name__}_cache"
            if not hasattr(self, cache_name):
                setattr(self, cache_name, lru_cache(None)(method.__get__(self, type(self))))
            return getattr(self, cache_name)(*args, **kwargs)
        return wrapper
    return decorator
