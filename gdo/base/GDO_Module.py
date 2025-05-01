import importlib
import os

from typing_extensions import Self

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page
    from gdo.base.Method import Method

from packaging.version import Version

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException
from gdo.base.GDO import GDO
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.base.Util import Files, href, err, msg
from gdo.base.WithModuleConfig import WithModuleConfig


class GDO_Module(WithModuleConfig, GDO):
    CORE_VERSION = Version("8.0.1")
    CORE_REV = "PyGDOv8.0.1-r1388"

    METHOD_CACHE = {}

    _priority: int
    _inited: bool
    _license: str

    __slots__ = (
        '_priority',
        '_inited',
        '_license',
    )

    @classmethod
    def instance(cls) -> Self:
        return ModuleLoader.instance().get_module(cls.get_name())

    def __init__(self):
        super().__init__()
        self._priority = 50
        self._inited = False
        self._license = 'PyGDOv8'

    def __repr__(self):
        return self.__class__.__name__

    def is_core_module(self) -> bool:
        from gdo.core.module_core import module_core
        return self.get_name() in module_core.instance().gdo_dependencies()

    def gdo_licenses(self) -> list[str]:
        return ['LICENSE']

    def gdo_install(self):
        pass

    def gdo_init(self):
        pass

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        pass

    def gdo_subscribe_events(self):
        pass

    def gdo_load_scripts(self, page: 'GDT_Page'):
        pass

    def gdo_is_site_module(self) -> bool:
        return False

    @classmethod
    def get_name(cls):
        return cls.__name__[7:]

    @classmethod
    def gdo_table_name(cls) -> str:
        return 'gdo_module'

    def gdo_dependencies(self) -> list:
        return []

    def gdo_friendencies(self) -> list:
        return []

    def gdo_columns(self):
        from gdo.core.GDT_AutoInc import GDT_AutoInc
        from gdo.core.GDT_Bool import GDT_Bool
        from gdo.core.GDT_Name import GDT_Name
        from gdo.core.GDT_UInt import GDT_UInt
        return [
            GDT_AutoInc('module_id'),
            GDT_Name('module_name').not_null().writable(False).label('name'),
            GDT_Bool('module_enabled').not_null().initial('1').label('enabled'),
            GDT_UInt('module_priority').not_null().initial('50').writable(False),
        ]

    def gdo_cached(self) -> bool:
        return False

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

    def is_installable(self) -> bool:
        return True

    def init(self):
        if not self._inited:
            self.gdo_init()
            self.gdo_subscribe_events()
            self._inited = True
        pass

    def file_path(self, append=''):
        return Application.file_path(f"gdo/{self.get_name()}/{append}")

    def www_path(self, filename: str) -> str:
        return f"{Application.config('core.web_root')}gdo/{self.get_name()}/{filename}"

    def www_url(self, filename: str) -> str:
        return f"http://{Application.config('core.domain')}/gdo/{self.get_name()}/{filename}"

    def render_name(self):
        return t(f"module_{self.get_name()}")

    def get_methods(self) -> list['Method']:
        methods = []
        dirname = self.file_path('method')
        if Files.exists(dirname):
            for file_name in os.listdir(dirname):
                if not file_name.startswith('_'):
                    method = self.instantiate_method(file_name[:-3])
                    methods.append(method)
        return methods

    def get_method(self, name: str) -> 'Method':
        return self.instantiate_method(name)

    def instantiate_method(self, name: str) -> 'Method':
        module_path = f"gdo.{self.get_name()}.method.{name}"
        if method_class := self.METHOD_CACHE.get(module_path):
            return method_class()
        try:
            mn = importlib.import_module(module_path)
            method_class = getattr(mn, name, None)
            if not method_class:
                raise GDOMethodException(self.get_name(), name)
            self.METHOD_CACHE[module_path] = method_class
            return method_class()
        except ModuleNotFoundError:
            raise GDOMethodException(self.get_name(), name)

    def href(self, method_name: str, append: str = '', format: str = 'html'):
        return href(self.get_name(), method_name, append, format)

    ##########
    # Errors #
    ##########
    def err(self, key: str, args: list[str] = None):
        err(key, args, self.render_name())
        return self

    def msg(self, key: str, args: list[str] = None):
        msg(key, args, self.render_name())
        return self

    ##########
    # Assets #
    ##########
    def add_css(self, filename: str):
        from gdo.ui.GDT_Page import GDT_Page
        path = f"{self.www_path(filename)}?v={self.CORE_REV}"
        GDT_Page._css.append(path)
        return self

    def add_bower_css(self, filename: str):
        return self.add_css(f'node_modules/{filename}')

    def add_js(self, filename: str):
        from gdo.ui.GDT_Page import GDT_Page
        path = f"{self.www_path(filename)}?v={self.CORE_REV}"
        GDT_Page._js.append(path)
        return self

    def add_bower_js(self, filename: str):
        return self.add_js(f'node_modules/{filename}')

    def add_js_inline(self, code: str):
        from gdo.ui.GDT_Page import GDT_Page
        GDT_Page._js_inline += f"<script>\n{code}\n</script>\n"
        return self

    ##########
    # Events #
    ##########
    def gdo_after_delete(self, gdo):
        ModuleLoader.instance().after_delete(gdo)

    def subscribe(self, event_name: str, callback: callable, times: int = 2_000_000_000):
        Application.EVENTS.subscribe_times(event_name, callback, times)

    def get_description(self) -> str:
        return ''
