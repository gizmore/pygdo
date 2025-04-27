from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_String import GDT_String


class GDO_GDOTable(GDO):

    def gdo_persistent(self) -> bool:
        return True

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('gdot_id'),
            GDT_Module('gdot_module').not_null(),
            GDT_String('gdot_name').not_null(),
        ]

    @classmethod
    def register_table(cls, class_name: type[GDO]):
        if not cls.table().get_by('gdot_name', class_name.__name__):
            cls.blank({
                'gdot_module': class_name.gdo_module().get_id(),
                'gdot_name': class_name.__name__,
            }).insert()
