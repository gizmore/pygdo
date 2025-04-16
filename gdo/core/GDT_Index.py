from gdo.base.GDT import GDT
from gdo.base.WithName import WithName

class GDT_Index(WithName, GDT):

    _index_type: str
    _index_using: str
    _index_fields: tuple[str, ...]

    def __init__(self, name: str):
        super().__init__()
        self.name(name)
        self._index_fields = ()
        self._index_using = ''
        self._index_type = 'INDEX'

    def index_fields(self, *field_names: str):
        self._index_fields = field_names
        return self

    def index_using(self, using: str):
        self._index_using = using
        return self

    def index_type(self, index_type: str):
        self._index_type = index_type
        return self

    def unique(self):
        return self.index_type('UNIQUE')

    def fulltext(self):
        return self.index_type('FULLTEXT')

    def spatial(self):
        return self.index_type('SPATIAL')

    def using_btree(self):
        return self.index_using('BTREE')

    def using_hash(self):
        return self.index_using('HASH')

    def gdo_column_define(self) -> str:
        if not self._index_fields:
            raise RuntimeError(f"GDT_Index {self._name} has no index_fields() set.")
        fields = ', '.join(f'`{f}`' for f in self._index_fields)
        using = f" USING {self._index_using}" if self._index_using else ''
        return f"{self._index_type} `{self.get_name()}` ({fields}){using}"
