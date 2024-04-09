from gdo.core import GDO


class Cache:
    cache: dict[GDO] = {}

    @classmethod
    def table_for(cls, gdo):
        if gdo not in cls.cache:
            cls.cache[gdo] = gdo()
            cls.cache[gdo]._is_table = True
        return cls.cache[gdo]
