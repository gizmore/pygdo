from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time


class GDT_Deleted(GDT_Timestamp):

    def __init__(self, name):
        super().__init__(name)

    def gdo_before_delete(self, gdo):
        gdo.set_val(self._name, Time.get_date())
        return self
