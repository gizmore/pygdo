from gdo.core import GDO
from gdo.core.GDT import GDT


class Cache:
    CACHE: dict[str, GDO] = {}
    CCACHE: dict[str, list[GDT]] = {}

    @classmethod
    def table_for(cls, gdo: GDO):
        cn = gdo
        if cn not in cls.CACHE:
            cls.CACHE[cn] = gdo()
            cls.CACHE[cn]._is_table = True
            cls.CCACHE[cn] = cls.build_ccache(gdo)
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

