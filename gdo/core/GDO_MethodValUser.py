from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String


class GDO_MethodValUser(GDO):

    def gdo_columns(self) -> list[GDT]:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_User import GDO_User
        return [
            GDT_Object('mv_method').table(GDO_Method.table()).primary().cascade_delete(),
            GDT_Object('mv_user').table(GDO_User.table()).primary().cascade_delete(),
            GDT_Name('mv_key').primary(),
            GDT_String('mv_val'),
        ]

    def get_val(self):
        return self.gdo_val('mv_val')
