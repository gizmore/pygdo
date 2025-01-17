from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time


class GDT_Created(GDT_Timestamp):

    def gdo_before_create(self, gdo):
        gdo.set_val(self._name, Time.get_date())
        return self
