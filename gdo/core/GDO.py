from gdo.core.Cache import Cache
from gdo.core.GDT import GDT
from gdo.db.Query import Query


class GDO(GDT):

    _vals: dict
    _dirty: list
    _is_table: bool

    def __init__(self):
        super().__init__()
        self._vals = {}
        self._dirty = []
        self._is_table = False

    @classmethod
    def table(cls):
        return Cache.table_for(cls)

    @classmethod
    def blank(cls, vals: dict):
        return 1

    def gdo_primary_key_column(self):
        return self.gdo_columns()[0]

    def gdo_columns(self):
        return []

    def get(self, key):
        return self._vals[key]

    def set(self, key, val, dirty=True):
        if key in self._vals.keys():
            if val == self._vals[key]:
                dirty = False
        self._vals[key] = val
        return self.dirty(key, dirty)

    def gdo_table_name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls):
        return cls.__name__

    def dirty(self, key, dirty=True):
        if key in self._dirty:
            if not dirty:
                self._dirty.remove(key)
        else:
            if dirty:
                self._dirty.append(key)
        return self

    def query(self):
        return Query().gdo(self)

    def select(self) -> Query:
        return self.query().select()

    def count_where(self, where='1'):
        col = self.select().where(where).exec().fetch_val()
        if col is None:
            return 0
        return int(col)
