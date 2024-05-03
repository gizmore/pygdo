from gdo.base.GDO import GDO
from gdo.core.GDT_UInt import GDT_UInt


class GDT_Object(GDT_UInt):
    _table: GDO

    def __init__(self, name):
        super().__init__(name)

    def table(self, gdo: GDO):
        self._table = gdo
        return self

    def gdo_column_define(self) -> str:
        pk = self._table.primary_key_column()
        define = pk.gdo_column_define()
        define = define.replace(pk._name, self._name)
        define = define.replace(' NOT NULL', '')
        define = define.replace(' PRIMARY KEY', '')
        define = define.replace(' AUTO_INCREMENT', '')
        #$define = preg_replace('#,FOREIGN KEY .* ON UPDATE (?:CASCADE|RESTRICT|SET NULL)#', '', $define);
        return define

    def to_val(self, value) -> str:
        return value.get_id() if value is not None else None

    def to_value(self, val: str):
        return self._table.get_by_id(val) if val is not None else None

