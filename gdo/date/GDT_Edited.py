from gdo.date.GDT_Created import GDT_Created
from gdo.date.Time import Time


class GDT_Edited(GDT_Created):

    _on_created: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.label('edited')
        self.not_null(False)
        self._on_created = False

    def edit_on_created(self, on_created: bool=True):
        self._on_created = on_created
        return self

    def gdo_before_create(self, gdo):
        if self._on_created:
            self.gdo_before_create(gdo)

    def gdo_before_update(self, gdo):
        gdo.set_val(self._name, Time.get_date())
