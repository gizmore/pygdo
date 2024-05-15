from gdo.base.GDO import GDO


class WithObject:
    _table: GDO
    _on_delete: str

    def table(self, gdo: GDO):
        self._table = gdo
        self._on_delete = 'RESTRICT'
        return self

    def cascade_delete(self):
        self._on_delete = 'CASCADE'
        return self

    def cascade_null(self):
        self._on_delete = 'SET NULL'
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

    def column_define_fk(self) -> str:
        t = self._table
        pk = t.primary_key_column()
        tn = t.gdo_table_name()
        return f"FOREIGN KEY({self._name}) REFERENCES {tn}({pk.get_name()}) ON UPDATE CASCADE ON DELETE {self._on_delete}"
