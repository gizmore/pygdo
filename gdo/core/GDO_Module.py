import os.path

from gdo.core.Application import Application
from gdo.core.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Name import GDT_Name
from gdo.core.ModuleLoader import ModuleLoader
from gdo.core.Trans import Trans, t


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

    def gdo_columns(self):
        return [
            GDT_AutoInc('module_id'),
            GDT_Name('module_name').not_null(),
            GDT_Bool('module_enabled').not_null().initial('1')
        ]

    def gdo_classes(self):
        return []

    def get_by_name(self, modulename: str):
        return self.get_by_vars({'module_name': modulename})

    def installed(self):
        return self.persisted()

    def is_enabled(self):
        return self.get('module_enabled') == '1'

    def init_language(self):
        Trans.add_language(self.file_path(f"lang/{self.get_name()}"))

    def gdo_install(self):
        pass

    def gdo_init(self):
        pass

    def file_path(self, append=''):
        return Application.file_path(f"gdo/{self.get_name()}/{append}")

    def render_name(self):
        return t(f"module_{self.get_name()}")
