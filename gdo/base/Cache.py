import functools
import hashlib

import msgpack
from redis import Redis

from gdo.base import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.base.WithSerialization import WithSerialization


class Cache:
    """
    The wonderful pygdo cache in 187 lines of code.
    There are 3 caches:
    1) TCACHE holds GDO.table() objects to re-use GDTs
    2) CCACHE holds GDO.gdo_columns() GDTs to re-use them
    3) REDIS O/F/CACHE holds an object - and arbitrary kv store
    (c) 2025 by gizmore@wechall.net and chappy@chappy-bot.net
    """
    HITS = 0
    MISS = 0
    UPDATES = 0
    REMOVES = 0

    TCACHE: dict[str, GDO] = {}  # class => GDO table mapping
    CCACHE: dict[str, list[GDT]] = {}  # class => GDO table GDT columns mapping
    REDIS: Redis = None

    @classmethod
    def init(cls, host: str = 'localhost', port: int = 6379, db: int = 0):
        cls.REDIS = Redis(host=host, port=port, db=db, decode_responses=False)

    @classmethod
    def clear(cls):
        cls.TCACHE = {}
        cls.CCACHE = {}
        cls.REDIS.flushdb()
        Files.empty_dir(Application.file_path('cache/'))

    @classmethod
    def clear_stats(cls):
        cls.UPDATES = cls.MISS = cls.REMOVES = cls.HITS = 0

    #############
    # T/C/Cache #
    #############

    @classmethod
    def table_for(cls, gdo_klass: type[GDO]):
        cn = gdo_klass
        if cn not in cls.TCACHE:
            cls.TCACHE[cn] = gdo_klass()
            cls.CCACHE[cn] = cls.build_ccache(gdo_klass)
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
    def column_for(cls, gdo: GDO, key: str) -> GDT:
        for gdt in cls.columns_for(gdo):
            if gdt.get_name() == key:
                return gdt

    ##########
    # OCACHE #
    ##########

    @classmethod
    def obj_for(cls, gdo: GDO) -> GDO:
        if gdo.gdo_cached():
            gid = gdo.get_id()
            cn = gdo.gdo_table_name()
            cached = cls.get(cn, gid)
            if not cached:
                cls.set(cn, gid, gdo)
            elif gdo != cached:
                gdo2 = gdo
                gdo = cached
                gdo._vals.update(gdo2._vals)
                gdo.all_dirty(False)
            else:
                gdo = cached
        return gdo

    @classmethod
    def update_for(cls, gdo: GDO):
        cls.set(gdo.gdo_table_name(), gdo.get_id(), gdo)
        return gdo

    @classmethod
    def obj_search(cls, gdo: GDO, vals: dict, delete: bool = False):
        if gdo.gdo_cached():
            cn = gdo.gdo_table_name()
            cursor = 0
            while True:
                cursor, keys = cls.REDIS.scan(cursor, match=f"{cn}:*")
                for key in keys:
                    key = key.decode()
                    if obj := cls.get(key):
                        found = True
                        for k, v in vals.items():
                            if obj.gdo_val(k) != v:
                                found = False
                                break
                        if found:
                            cls.HITS += 1
                            if delete:
                                cls.remove(key)
                            return obj
                if cursor == 0:
                    break
            cls.MISS += 1

    ##########
    # FCACHE #
    ##########

    @classmethod
    def get(cls, key: str, args_key: str = None, default: any = None):
        key = f"{key}:{args_key}" if args_key else key
        if packed := cls.REDIS.get(key):
            cls.HITS += 1
            return WithSerialization.gdounpack(packed)
        cls.MISS += 1
        return default

    @classmethod
    def set(cls, key: str, args_key: str | None, value: WithSerialization):
        if isinstance(value, WithSerialization):
            value = value.gdopack()
        else:
            value = msgpack.dumps(value)
        key = f"{key}:{args_key}" if args_key else key
        cls.REDIS.set(key, value)
        cls.UPDATES += 1

    @classmethod
    def remove(cls, key: str = None, args_key: str = None):
        if key is None:
            cls.REDIS.flushdb()
        elif args_key is None:
            cursor = 0
            while True:
                cursor, keys = cls.REDIS.scan(cursor, match=f"{key}:*")
                if keys:
                    cls.REMOVES += 1
                    cls.REDIS.delete(*keys)
                if cursor == 0:
                    break
        else:
            cls.REMOVES += 1
            redis_key = f"{key}:{args_key}"
            cls.REDIS.delete(redis_key)


#############
# Decorator #
#############

def _hash_args(args, kwargs):
    # todo sort kwargs by key?
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
