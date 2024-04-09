from gdo.core.Application import Application


class Result:
    _result: object
    _table: object

    def __init__(self, result, gdo):
        self._result = result
        self._table = gdo

    def fetch_row(self):
        return Application.DB.fetch_row()[0]

    def fetch_val(self):
        row = self.fetch_row()
        if row is None:
            return None
        return row[0]
