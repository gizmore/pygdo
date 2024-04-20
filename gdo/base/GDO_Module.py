import importlib
import os

from packaging.version import Version

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException
from gdo.base.GDO import GDO
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import Trans, t
from gdo.base.Util import Files, href, err, msg
from gdo.base.WithModuleConfig import WithModuleConfig


class GDO_Module(WithModuleConfig, GDO):
    CORE_VERSION = Version("8.0.0")
    CORE_REV = "PyGDOv8-0.0-r1000"

    _priority: int
    _inited: bool

    @classmethod
    def instance(cls):
        return ModuleLoader.instance().get_module(cls.get_name())

    def __init__(self):
        super().__init__()
        self._priority = 50
        self._inited = False

    def gdo_install(self):
        pass

    def gdo_init(self):
        pass

    def gdo_init_sidebar(self, page):
        pass

    def gdo_load_scripts(self, page):
        pass

    @classmethod
    def get_name(cls):
        return cls.__name__[7:]

    def gdo_table_name(self) -> str:
        return 'gdo_module'

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

    def init(self):
        if not self._inited:
            self.gdo_init()
            self._inited = True
        pass

    def init_language(self):
        Trans.add_language(self.file_path(f"lang/{self.get_name()}"))

    def file_path(self, append=''):
        return Application.file_path(f"gdo/{self.get_name()}/{append}")

    def www_path(self, filename: str) -> str:
        return f"{Application.config('core.web_root')}gdo/{self.get_name()}/{filename}"

    def www_url(self, filename: str) -> str:
        return f"http://{Application.config('core.domain')}/gdo/{self.get_name()}/{filename}"

    def render_name(self):
        return t(f"module_{self.get_name()}")

    def get_methods(self) -> list[Method]:
        methods = []
        dirname = self.file_path('method')
        if Files.exists(dirname):
            for file_name in os.listdir(dirname):
                full_path = os.path.join(dirname, file_name)
                if not file_name.startswith('_'):
                    method = self.instantiate_method(file_name[:-3])
                    methods.append(method)
        return methods

    def get_method(self, name: str) -> Method:
        return self.instantiate_method(name)

    def instantiate_method(self, name):
        try:
            mn = importlib.import_module("gdo." + self.get_name() + ".method." + name)
            return mn.__dict__[name]()
        except ModuleNotFoundError as ex:
            raise GDOMethodException(self.get_name(), name)

    def href(self, method_name: str, append: str = '', format: str = 'html'):
        return href(self.get_name(), method_name, append, format)

    ##########
    # Errors #
    ##########
    def err(self, key: str, args: list[str] = None):
        err(key, args, self.get_name())
        return self

    def msg(self, key: str, args: list[str] = None):
        msg(key, args, self.get_name())
        return self

    ##########
    # Assets #
    ##########
    def add_css(self, filename: str):
        from gdo.ui.GDT_Page import GDT_Page
        path = f"{self.www_path(filename)}?v={self.CORE_REV}"
        GDT_Page.instance()._css.append(path)
        return self

    def add_js(self, filename: str):
        from gdo.ui.GDT_Page import GDT_Page
        path = self.www_path(filename)
        GDT_Page.instance()._js.append(path)
        return self

    def add_js_inline(self, code: str):
        from gdo.ui.GDT_Page import GDT_Page
        GDT_Page.instance()._js_inline += f"<script>{code}</script>\n"
        return self
