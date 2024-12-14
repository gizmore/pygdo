from gdo.base.GDT import GDT
from gdo.base.WithName import WithName


class GDT_Unique(WithName, GDT):

    _column_names: list[str]

    def __init__(self, name: str):
        super().__init__()
        self.name(name)
        self._column_names = []

    def unique_columns(self, *column_names: str):
        self._column_names.extend(column_names)
        return self
