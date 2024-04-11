from gdo.core.GDT_UInt import GDT_UInt


class GDT_AutoInc(GDT_UInt):

    def __init__(self, name: str):
        super().__init__(name)
        self.primary()

    def gdo_column_define(self) -> str:
        return f"{self._name} {self.gdo_column_define_size()}INT UNSIGNED NOT NULL AUTO_INCREMENT"
