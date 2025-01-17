import functools
import hashlib

from gdo.base import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Files


class Cache:
    TCACHE: dict[str, GDO] = {}  # class => GDO table mapping
    CCACHE: dict[str, list[GDT]] = {}  # class => GDO table columns mapping
    OCACHE: dict[str, dict[str, GDO]] = {}  # id => GDO object cache mapping
    FCACHE = {}  # @gdo_cached("key") store

    @classmethod
    def clear(cls):
        cls.TCACHE = {}
        cls.CCACHE = {}
        cls.OCACHE = {}
        cls.FCACHE = {}
        Files.empty_dir(Application.file_path('cache/'))

    @classmethod
    def table_for(cls, gdo: GDO):
        cn = gdo
        if cn not in cls.TCACHE:
            cls.TCACHE[cn] = gdo()
            cls.CCACHE[cn] = cls.build_ccache(gdo)
            cls.OCACHE[cn] = {}
        return cls.TCACHE[gdo]

    @classmethod
    def columns_for(cls, gdo: GDO):
        cls.table_for(gdo)
        return cls.CCACHE[gdo]

    @classmethod
    def build_ccache(cls, gdo: GDO):
        cache = []
        columns = cls.TCACHE[gdo].gdo_columns()
        for column in columns:
            cache.append(column)
            cache.extend(column.gdo_components())
        return cache

    @classmethod
    def obj_for(cls, gdo: GDO) -> GDO:
        if gdo.gdo_cached():
            gid = gdo.get_id()
            cn = gdo.__class__
            if gid not in cls.OCACHE[cn]:
                cls.OCACHE[cn][gid] = gdo
            else:
                gdo2 = gdo
                gdo = cls.OCACHE[cn][gid]
                gdo._vals.update(gdo2._vals)
                gdo.all_dirty(False)
        return gdo

    @classmethod
    def column_for(cls, gdo: GDO, key: str) -> GDT:
        for gdt in cls.columns_for(gdo):
            if gdt.get_name() == key:
                return gdt

    @classmethod
    def obj_search(cls, gdo: GDO, vals: dict, delete: bool = False):
        cn = gdo.__class__
        if gdo.gdo_cached():
            for gid, obj in cls.OCACHE[cn].items():
                found = True
                for key, val in vals.items():
                    if obj.gdo_val(key) != val:
                        found = False
                        break
                if found:
                    if delete:
                        del cls.OCACHE[cn][gid]
                    return obj

    ##########
    # FCache #
    ##########

    @classmethod
    def get(cls, key: str, args_key: str, default: any = None):
        return cls.FCACHE.get(key, {}).get(args_key, default)

    @classmethod
    def set(cls, key: str, args_key: str, value: any):
        if key not in cls.FCACHE:
            cls.FCACHE[key] = {}
        cls.FCACHE[key][args_key] = value
        return value

    @classmethod
    def remove(cls, key: str = None, args_key: str = None):
        if key is None:
            cls.FCACHE.clear()
        elif args_key is None:
            cls.FCACHE.pop(key, None)
        else:
            cls.FCACHE.get(key, {}).pop(args_key, None)


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
