from gdo.core.GDO import GDO
from gdo.core.GDO_Module import GDO_Module
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String


class GDO_ModuleVar(GDO):

    def gdo_columns(self):
        return [
            GDT_Object('mv_module').table(GDO_Module.table()).primary().not_null(),
            GDT_Name('mv_key').not_null().primary(),
            GDT_String('mv_value'),
        ]
