import importlib
import os

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException
from gdo.base.GDO import GDO
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import Trans, t
from gdo.base.Util import Files


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
        from gdo.core.GDT_AutoInc import GDT_AutoInc
        from gdo.core.GDT_Bool import GDT_Bool
        from gdo.core.GDT_Name import GDT_Name
        return [
            GDT_AutoInc('module_id'),
            GDT_Name('module_name').not_null(),
            GDT_Bool('module_enabled').not_null().initial('1')
        ]

    def gdo_classes(self):
        return []

    def get_by_name(self, modulename: str, enabled: bool = None):
        vals = {'module_name': modulename}
        if isinstance(enabled, bool):
            vals['module_enabled'] = f"%i" % enabled
        return self.get_by_vals(vals)

    def installed(self):
        return self.is_persisted()

    def is_enabled(self):
        return self.gdo_val('module_enabled') == '1'

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

    def get_methods(self) -> list[Method]:
        methods = []
        dirname = self.file_path('method')
        if Files.exists(dirname):
            for file_name in os.listdir(dirname):
                full_path = os.path.join(dirname, file_name)
                if not file_name.startswith('_'):
                    method = self.instanciate_method(file_name[:-3])
                    methods.append(method)
        return methods

    def get_method(self, name: str) -> Method:
        return self.instanciate_method(name)

    def instanciate_method(self, name):
        try:
            mn = importlib.import_module("gdo." + self.get_name() + ".method." + name)
            return mn.__dict__[name]()
        except ModuleNotFoundError as ex:
            raise GDOMethodException(self.get_name(), name)

    # def instanciate_method(self, file_path):
    #     module_name = os.path.basename(file_path)[:-3]  # Remove the .py extension
    #     spec = importlib.util.spec_from_file_location(module_name, file_path)
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)
    #     for name in dir(module):
    #         obj = getattr(module, name)
    #         if isinstance(obj, type) and name == module_name:
    #             return obj()
    #
    #     return None

