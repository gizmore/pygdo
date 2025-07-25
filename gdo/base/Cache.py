import hashlib
import functools
import zlib

import msgspec.msgpack
from redis import Redis
from functools import lru_cache, wraps

from gdo.base import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.base.WithSerialization import WithSerialization


class Cache:
    """
    The wonderful pygdo cache in 303 lines of code.
    There are 4 caches:
    1) TCACHE holds GDO.table() objects to re-use GDTs.
    2) CCACHE holds GDO.gdo_columns() GDTs to re-use them.
    2) PCACHE holds PK GDO.gdo_columns() GDTs to re-use them.
    3) OCACHE holds GDO entities for single identity cache.
    3) REDIS (FCACHE) is the tad slower process shared memory cache.
    (c) 2025 by gizmore@wechall.net and chappy@chappy-bot.net.
    """
    #PYPP#START#
    HITS = 0
    MISS = 0
    UPDATES = 0
    REMOVES = 0
    THITS = 0 # template cache hits
    VHITS = 0 # gdo_values cache hits
    OHITS = 0 # OCACHE hits
    #PYPP#END#

    TCACHE: dict[str, GDO] = {}             # class_name => GDO.table() mapping
    CCACHE: dict[str, dict[str, GDT]] = {}  # class_name => GDO.gdo_columns() mapping
    PCACHE: dict[str, list[GDT]] = {}       # class_name => GDO.gdo_columns() PK mapping
    OCACHE: dict[str, dict[str, GDO]] = {}  # table_name => dict[id, GDO] mapping
    RCACHE: Redis = None                    # key => dict[key, WithSerialization] mapping
    NCACHE: list[str] = []                  # list of non persistent GDO table names

    ZLIB_LEVEL: int = -1

    @classmethod
    def init(cls, enabled: bool = False, host: str = 'localhost', port: int = 6379, db: int = 0, uds: str='', zlib_level: int=-1):
        if enabled:
            cls.ZLIB_LEVEL = zlib_level
            if uds:
                cls.RCACHE = Redis(unix_socket_path=uds, decode_responses=False)
            else:
                cls.RCACHE = Redis(host=host, port=port, db=db, decode_responses=False)

    @classmethod
    def clear(cls):
        cls.TCACHE = {}
        cls.CCACHE = {}
        cls.PCACHE = {}
        cls.clear_ocache()
        if cls.RCACHE:
            cls.RCACHE.flushdb()
        Files.empty_dir(Application.file_path('cache/'))

    #PYPP#START#
    @classmethod
    def clear_stats(cls):
        cls.UPDATES = cls.MISS  = cls.REMOVES = cls.HITS = 0
        cls.VHITS   = cls.OHITS = cls.THITS = 0
    #PYPP#END#

    @classmethod
    def clear_ocache(cls):
        """
        Clear request OCACHE for non persistent GDO
        """
        for tn in cls.NCACHE:
            cls.OCACHE[tn] = {}

    #############
    # T/C/Cache #
    #############

    @classmethod
    def table_for(cls, gdo_klass: type[GDO]):
        cn = gdo_klass
        if not (gdo := cls.TCACHE.get(cn)):
            cls.TCACHE[cn] = gdo = gdo_klass()
            cls.CCACHE[cn] = cls.build_ccache(gdo_klass)
            cls.PCACHE[cn] = cls.build_pkcache(gdo_klass)
            if gdo.gdo_cached():
                tn = gdo.gdo_table_name()
                cls.OCACHE[tn] = {}
                if not gdo.gdo_persistent():
                    cls.NCACHE.append(tn)
        return gdo

    @classmethod
    def build_ccache(cls, gdo_klass: type[GDO]) -> dict[str,GDT]:
        cache = {}
        for column in cls.TCACHE[gdo_klass].gdo_columns():
            cache[column.get_name()] = column
            for gdt in column.gdo_components():
                cache[gdt.get_name()] = gdt
        return cache

    @classmethod
    def build_pkcache(cls, gdo_klass: type[GDO]) -> list[GDT]:
        cache = []
        have_designated_pk = False
        for column in cls.CCACHE[gdo_klass].values():
            if column.is_primary():
                cache.append(column)
                have_designated_pk = True
        if not have_designated_pk:
            cache = list(cls.CCACHE[gdo_klass].values())
        return cache


    @classmethod
    def columns_for(cls, gdo_klass: type[GDO]) -> dict[str,GDT]:
        cls.table_for(gdo_klass)
        return cls.CCACHE[gdo_klass]

    @classmethod
    def column_for(cls, gdo_klass: type[GDO], key: str) -> GDT|None:
        return cls.columns_for(gdo_klass).get(key)

    @classmethod
    def pk_columns_for(cls, gdo_klass: type[GDO]) -> list[GDT]:
        cls.table_for(gdo_klass)
        return cls.PCACHE[gdo_klass]

    ##########
    # OCACHE #
    ##########

    @classmethod
    def obj_for(cls, gdo: GDO, rcached: dict[str,str]|None = None, after_write: bool = False) -> GDO:
        if gdo.gdo_cached():
            gid = gdo.get_id()
            cn = gdo.gdo_table_name()

            if ocached := cls.OCACHE[cn].get(gid):
                if after_write:
                    ocached.vals(gdo._vals)
                if rcached:
                    ocached.vals(rcached)
                return ocached.all_dirty(False)

            if after_write:
                cls.OCACHE[cn][gid] = gdo
                gdo._values = {}
                return gdo

            if rcached:
                gdo.vals(rcached)
            elif rcached := cls.get(cn, gid):
                gdo.set_vals(rcached)
            else:
                if not after_write:
                    cls.set(cn, gid, gdo._vals)

            cls.OCACHE[cn][gid] = gdo

        return gdo.all_dirty(False)

    @classmethod
    def update_for(cls, gdo: GDO) -> GDO:
        cls.set(gdo.gdo_table_name(), gdo.get_id(), gdo._vals)
        return cls.obj_for(gdo, None, True)

    @classmethod
    def obj_search_id(cls, gdo: GDO, vals: dict, delete: bool = False) -> GDO:
        gid = ":".join(v for v in vals.values())
        if delete:
            cls.obj_search_gid(gdo, gid, delete)
            return gdo
        return cls.obj_search_gid(gdo, gid, delete)

    @classmethod
    def obj_search_gid(cls, gdo: GDO, gid: str, delete: bool = False) -> GDO:
        tn = gdo.gdo_table_name()
        if ocached := cls.OCACHE[tn].get(gid):
            cls.OHITS += 1 #PYPP#DELETE#
            if delete:
                del cls.OCACHE[tn][gid]
                cls.remove(tn, gid)
            else:
                return ocached
        if rcached := cls.get(tn, gid):
            if delete:
                cls.remove(tn, gid)
            else:
                return cls.obj_for(gdo.blank(rcached, False), rcached, False).my_id(gid)
        return None

    @classmethod
    def obj_search(cls, gdo: GDO, vals: dict, delete: bool = False) -> GDO:
        return cls.obj_search_pygdo(gdo, vals, delete)

    @classmethod
    def obj_search_pygdo(cls, gdo: GDO, vals: dict, delete: bool = False) -> GDO:
        if gdo.gdo_cached():
            cn = gdo.gdo_table_name()
            for oc in cls.OCACHE[cn].values():
                found = True
                for k, v in vals.items():
                    if oc.gdo_val(k) != v:
                        found = False
                        break
                if found:
                    cls.OHITS += 1 #PYPP#DELETE#
                    if delete:
                        gid = oc.get_id()
                        cls.remove(gid)
                        del cls.OCACHE[cn][gid]
                    return oc
        return None

    @classmethod
    def obj_search_redis(cls, gdo: GDO, vals: dict, delete: bool = False) -> GDO:
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
                            if rc[k] != v:
                                found = False
                                break
                        if found:
                            cls.HITS += 1 #PYPP#DELETE#
                            # gdo.set_vals(rc)
                            gdo.all_dirty(False)
                            if delete:
                                cls.remove(key)
                                id = gdo.get_id()
                                if id in cls.OCACHE[cn]:
                                    del cls.OCACHE[cn][id]
                                    return None
                            return cls.obj_for(gdo, rc, False)
                if cursor == 0:
                    break
            cls.MISS += 1 #PYPP#DELETE#
        return None

    ##########
    # FCACHE #
    ##########

    @classmethod
    def get(cls, key: str, args_key: str = None, default: any = None) -> any:
        if cls.RCACHE:
            key = f"{key}:{args_key}" if args_key else key
            if packed := cls.RCACHE.get(key):
                cls.HITS += 1 #PYPP#DELETE#
                data = zlib.decompress(packed) if cls.ZLIB_LEVEL >= 0 else packed
                return WithSerialization.gdounpack(data)
            cls.MISS += 1 #PYPP#DELETE#
        return default

    @classmethod
    def set(cls, key: str, args_key: str | None, value: any):
        if cls.RCACHE:
            if hasattr(value, 'gdopack'):
                value = value.gdopack()
            else:
                value = msgspec.msgpack.encode(value)
            cls.UPDATES += 1 #PYPP#DELETE#
            key = f"{key}:{args_key}" if args_key else key
            data = zlib.compress(value, cls.ZLIB_LEVEL) if cls.ZLIB_LEVEL >= 0 else value
            cls.RCACHE.set(key, data)

    @classmethod
    def remove(cls, key: str = None, args_key: str = None):
        if cls.RCACHE:
            if key is None:
                cls.REMOVES += 1 #PYPP#DELETE#
                cls.RCACHE.flushdb()
            elif args_key is None:
                cursor = 0
                while True:
                    cursor, keys = cls.RCACHE.scan(cursor, match=f"{key}:*")
                    if keys:
                        cls.REMOVES += 1 #PYPP#DELETE#
                        cls.RCACHE.delete(*keys)
                    if cursor == 0:
                        break
            else:
                cls.REMOVES += 1 #PYPP#DELETE#
                redis_key = f"{key}:{args_key}"
                cls.RCACHE.delete(redis_key)

    @classmethod
    def reload(cls, table_name: str, gid: str):
        cls.OCACHE[table_name][gid].reload()


#############
# Decorator #
#############

def _hash_args(args, kwargs):
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
