from gdo.base.Application import Application
from gdo.core.GDT_UInt import GDT_UInt


class GDT_AutoInc(GDT_UInt):

    def __init__(self, name: str):
        super().__init__(name)
        self.primary()
        self.label('id')
        self.initial('0')
        self.not_null(True)

    def gdo_column_define(self) -> str:
        return f"{self._name} {self.gdo_column_define_size()}INT UNSIGNED NOT NULL AUTO_INCREMENT"

    def gdo_after_create(self, gdo):
        key = gdo.primary_key_column().get_name()
        val = str(gdo._last_id)
        gdo.set_val(key, val, False)
        gdo._my_id = val

    def gdo_after_delete(self, gdo):
        key = gdo.primary_key_column().get_name()
        gdo.set_val(key, '0', False)
