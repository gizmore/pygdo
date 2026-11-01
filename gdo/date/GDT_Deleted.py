from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time


class GDT_Deleted(GDT_Timestamp):
    """Turn individual GDO deletes into timestamp updates.

    This field does not hide deleted rows from selects or direct lookups;
    consumers must filter and authorize them explicitly. Bulk deletes bypass
    hooks and remain hard deletes.
    """

    def __init__(self, name):
        super().__init__(name)
        self.label('deleted')
        self.icon('clock')

    def gdo_before_delete(self, gdo):
        gdo.set_val(self._name, Time.get_date())
        return self

    def gdo_before_delete_query(self, gdo, query):
        from gdo.base.Query import Type
        query.type(Type.UPDATE).set_vals(gdo.dirty_vals())
