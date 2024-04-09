from gdo.core.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.core.ModuleLoader import ModuleLoader


class GDO_Module(GDO):
    _priority: int

    @classmethod
    def instance(cls):
        return ModuleLoader.instance().get_module(cls.get_name())

    def __init__(self):
        super().__init__()
        self._priority = 50

    @classmethod
    def get_name(cls):
        return cls.__name__[7:]

    def gdo_table_name(self) -> str:
        return 'GDO_Module'

    def gdo_dependencies(self) -> list:
        return []

    @classmethod
    def gdo_columns(cls):
        return [
            GDT_AutoInc('module_id'),
            GDT_Name('module_name').not_null(),

        ]

    def gdo_init(self):
        return self

    def gdo_classes(self):
        return []
