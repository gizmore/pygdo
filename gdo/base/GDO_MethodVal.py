from gdo.base.GDO import GDO
from gdo.base.GDO_Method import GDO_Method
from gdo.base.GDT import GDT
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String


class GDO_MethodVal(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_Object('mv_method').table(GDO_Method.table()).primary(),
            GDT_Name('mv_key').primary(),
            GDT_String('mv_val'),
        ]
