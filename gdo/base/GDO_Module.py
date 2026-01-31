import importlib
from functools import lru_cache, cached_property
from glob import glob

from typing_extensions import Self

from typing import TYPE_CHECKING, Type, Iterator

from gdo.base.util.href import href

if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page
    from gdo.base.Method import Method

from packaging.version import Version

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException
from gdo.base.GDO import GDO
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.base.Util import Files, err, msg, Strings
from gdo.base.WithModuleConfig import WithModuleConfig


class GDO_Module(WithModuleConfig, GDO):
    CORE_VERSION = Version("8.0.2")
    CORE_REV = "PyGDOv8.0.2-r1263"

    METHOD_CACHE: dict[str,Type['Method']] = {}

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
        return ModuleLoader.instance().get_module(cls.__name__[7:])

    def __init__(self):
        super().__init__()
        self._priority = 50
        self._inited = False
        self._license = 'PyGDOv8'

    def __repr__(self):
        return self.__class__.__name__

    def is_core_module(self) -> bool:
        from gdo.core.module_core import module_core
        return self.get_name in module_core.instance().gdo_dependencies()

    def gdo_licenses(self) -> list[str]:
        return ['LICENSE']

    async def gdo_install(self):
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

    @cached_property
    def get_name(self):
        return self.__class__.__name__[7:]

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
        return Application.file_path(f"gdo/{self.get_name}/{append}")

    def www_path(self, filename: str) -> str:
        return f"{Application.config('core.web_root')}gdo/{self.get_name}/{filename}"

    def www_url(self, filename: str) -> str:
        return f"http://{Application.config('core.domain')}/gdo/{self.get_name}/{filename}"

    def render_name(self):
        return t(f"module_{self.get_name}")

    @lru_cache
    def get_method_klasses(self) -> dict[str,type['Method']]:
        methods = {}
        dirname = self.file_path('method')
        for file_name in glob(f"{dirname}/**/*", recursive=True):
            if not '__' in file_name and Files.is_file(file_name):
                path = Strings.substr_from(file_name, Application.file_path())
                mod_path = path.replace('/', '.')[:-3]
                name = Strings.rsubstr_from(mod_path, '.')
                mn = importlib.import_module(mod_path)
                klass = getattr(mn, name)
                methods[name] = klass
        return methods

    def get_methods(self) -> Iterator['Method']:
        for klass in self.get_method_klasses().values():
            yield klass().module(self)

    def get_method(self, name: str) -> 'Method':
        return self.instantiate_method(name)

    def instantiate_method(self, name: str) -> 'Method':
        klass = self.get_method_klasses().get(name)
        if not klass:
            raise GDOMethodException(self.get_name, name)
        return klass().module(self)

    def href(self, method_name: str, append: str = '', format: str = 'html'):
        return href(self.get_name, method_name, append, format)

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
    GDT_Page = None
    def gdt_page(self):
        if not self.__class__.GDT_Page:
            from gdo.ui.GDT_Page import GDT_Page
            self.__class__.GDT_Page = GDT_Page
        return self.__class__.GDT_Page

    def add_css(self, filename: str):
        path = f"{self.www_path(filename)}?v={self.CORE_REV}"
        self.gdt_page()._css.append(path)
        return self

    def add_bower_css(self, filename: str):
        return self.add_css(f'node_modules/{filename}')

    def add_js(self, filename: str):
        path = f"{self.www_path(filename)}?v={self.CORE_REV}"
        self.gdt_page()._js.append(path)
        return self

    def add_bower_js(self, filename: str):
        return self.add_js(f'node_modules/{filename}')

    def add_js_inline(self, code: str):
        self.gdt_page()._js_inline += f"<script>\n{code}\n</script>\n"
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
