from gdo.base import GDO
from gdo.base.GDT import GDT


class Cache:
    CACHE: dict[str, GDO] = {}
    CCACHE: dict[str, list[GDT]] = {}
    OCACHE: dict[str, dict[str, GDO]] = {}

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
            gdo = cls.OCACHE[cn][gid].set_vals(gdo._vals, False)
        return gdo

    @classmethod
    def column_for(cls, gdo: GDO, key: str) -> GDT:
        for gdt in cls.columns_for(gdo):
            if gdt.get_name() == key:
                return gdt

    @classmethod
    def obj_search(cls, gdo: GDO, vals: dict):
        cn = gdo.__class__
        for obj in cls.OCACHE[cn].values():
            found = True
            for key, val in vals.items():
                if obj.gdo_val(key) != val:
                    found = False
                    break
            if found:
                return obj
