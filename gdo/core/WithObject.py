from gdo.base.GDO import GDO
from gdo.base.Render import Render, Mode


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
        if not self.is_not_null():
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

    ### GDT_Object

    def to_val(self, value) -> str:
        return value.get_id() if value is not None else None

    def to_value(self, val: str):
        if val is None:
            return None
        return self.get_by_name(val)
        #        return self._table.get_by_id(val) if val is not None else None

    def get_gdo(self) -> GDO:
        return self.get_value()

    def query_gdos(self, val: str) -> list[GDO]:
        gdo = self._table.get_by_aid(val)
        return [gdo] if gdo else []

    def get_by_name(self, var: str) -> list[GDO] | GDO | None:
        gdos = self.query_gdos(var)
        if self._multiple:
            return gdos
        if len(gdos) == 0:
            return None
        if len(gdos) == 1:
            return gdos[0]

        firsts = []
        middles = {}
        for gdo in gdos:
            name = gdo.render_name()
            if name.lower() == var.lower():
                return gdo
            if name.lower().startswith(var.lower()):
                firsts.append(gdo)
            middles[name] = gdo

        if len(firsts) == 1:
            return firsts[0]
        if len(middles) == 1:
            return list(middles.values())[0]

        self.error('err_select_candidates', ('|'.join(middles.keys()),))
        return None

        ##########
        # Render #
        ##########

    def render_cli(self) -> str:
        gdo = self.get_gdo()
        if gdo is None:
            return ''
        if gdo.is_persisted():
            return f"{Render.bold(gdo.get_id(), Mode.CLI)}-{gdo.render_name()}"
        else:
            return gdo.render_name()

    def render_cell(self) -> str:
        return self.get_gdo().render_name()

        ############
        # Validate #
        ############

    def validate(self, val: str | None, value: any):
        if self.has_error():
            return False
        if value:
            return True
        if not super().validate(val, value):
            return False
        return True
