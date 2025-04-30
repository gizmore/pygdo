from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String


class reload_gdo(Method):
    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_String('class').not_null(),
            GDT_String('id').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        Cache.reload(self.param_val('class'), self.param_val('id'))
        return self.empty()
