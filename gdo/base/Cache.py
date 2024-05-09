from gdo.base import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Files


class Cache:
    CACHE: dict[str, GDO] = {}
    CCACHE: dict[str, list[GDT]] = {}
    OCACHE: dict[str, dict[str, GDO]] = {}

    @classmethod
    def clear(cls):
        cls.CACHE = {}
        cls.CCACHE = {}
        cls.OCACHE = {}
        Files.empty_dir(Application.file_path('cache/'))

    @classmethod
    def table_for(cls, gdo: GDO):
        cn = gdo
        if cn not in cls.CACHE:
            cls.CACHE[cn] = gdo()
            cls.CCACHE[cn] = cls.build_ccache(gdo)
            cls.OCACHE[cn] = {}
        return cls.CACHE[gdo]

    @classmethod
    def columns_for(cls, gdo: GDO):
        cls.table_for(gdo)
        return cls.CCACHE[gdo]

    @classmethod
    def build_ccache(cls, gdo: GDO):
        cache = []
        columns = cls.CACHE[gdo].gdo_columns()
        cache.extend(columns)
        return cache

    @classmethod
    def obj_for(cls, gdo: GDO) -> GDO:
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
