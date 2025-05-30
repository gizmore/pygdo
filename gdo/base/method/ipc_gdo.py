from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Serialize import GDT_Serialize, SerializeMode
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_TableName import GDT_TableName


class ipc_gdo(Method):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_TableName('table').not_null(),
            GDT_String('id').not_null(),
            GDT_Serialize('dirty').mode(SerializeMode.JSON),
        ]

    def gdo_execute(self) -> GDT:
        tn = self.param_val('table')
        gid = self.param_val('id')
        if gdo := Cache.OCACHE[tn].get(gid):
            if dirty := self.param_value('dirty'):
                gdo.set_vals(dirty, False)
            else:
                gdo.reload()
        return self.empty()
