from gdo.core.GDO import GDO
from gdo.core.GDO_Module import GDO_Module
from gdo.core.GDT_Object import GDT_Object


class GDO_ModuleVar(GDO):

    def gdo_columns(self):
        return [
            GDT_Object('mv_module').table(GDO_Module.table()).primary().not_null()
        ]

    def gdo_init(self):
        pass