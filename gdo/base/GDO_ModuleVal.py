from gdo.base.GDO import GDO


class GDO_ModuleVal(GDO):

    def gdo_columns(self):
        from gdo.base.GDO_Module import GDO_Module
        from gdo.core.GDT_Name import GDT_Name
        from gdo.core.GDT_Object import GDT_Object
        from gdo.core.GDT_String import GDT_String
        return [
            GDT_Object('mv_module').table(GDO_Module.table()).primary().cascade_delete(),
            GDT_Name('mv_key').not_null().primary(),
            GDT_String('mv_val'),
        ]

    def gdo_cached(self) -> bool:
        return False
