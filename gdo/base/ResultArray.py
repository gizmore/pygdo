from gdo.base.GDO import GDO
from gdo.base.Result import Result


class ResultArray(Result):
    _pos: int
    _data: list


    def __init__(self, data: list, gdo: GDO):
        self._table = gdo
        self._data = data
        self._pos = 0

    def fetch_row(self):
        if self._pos == len(self._data):
            return None
        row = self._data[self._pos]
        self._pos += 1
        return row._vals.values()

    def fetch_assoc(self):
        if self._pos == len(self._data):
            return None
        row = self._data[self._pos]
        self._pos += 1
        return dict(row._vals.items())

    def fetch_object(self):
        if self._pos == len(self._data):
            return None
        row = self._data[self._pos]
        self._pos += 1
        return row

