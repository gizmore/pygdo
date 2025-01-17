from gdo.date.GDT_Created import GDT_Created
from gdo.date.Time import Time


class GDT_Edited(GDT_Created):

    def gdo_before_update(self, gdo):
        gdo.set_val(self._name, Time.get_date())
        return self
