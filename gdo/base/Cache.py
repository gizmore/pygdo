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
            cls.CACHE[cn]._is_table = True
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
        for gdt in columns:
            cache.append(gdt)
        return cache

    @classmethod
    def obj_for(cls, gdo: GDO):
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
