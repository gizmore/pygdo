from gdo.core.GDT_UInt import GDT_UInt


class GDT_AutoInc(GDT_UInt):

    def gdo_column_define(self) -> str:
        return f"{self._name} {self.gdo_column_define_size()}INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY"
