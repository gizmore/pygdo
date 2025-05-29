from __future__ import annotations

import sys

from typing_extensions import Self

from typing import TYPE_CHECKING, Iterator

from gdo.base.Logger import Logger
from gdo.base.Trans import t

if TYPE_CHECKING:
    from gdo.base.Method import Method
    from gdo.base.GDO_Module import GDO_Module

import glob
import importlib

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOException, GDODBException
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.Result import ResultType
from gdo.base.Util import Files, html


class ModuleLoader:
    _cache: dict[str, 'GDO_Module'] # name
    _methods: dict[str, 'Method'] # trigger
    _enabled: list['GDO_Module']

    @classmethod
    def instance(cls) -> Self:
        return Application.LOADER

    def enabled(self) -> list['GDO_Module']:
        return self._enabled

    def reset(self):
        self._cache.clear()

    def gdo_import(self, name: str) -> 'GDO_Module':
        mn = importlib.import_module(f"gdo.{name}")
        if klass := mn.__dict__.get(f"module_{name}"):
            self._cache[name] = module = klass.blank({
                'module_name': name,
                'module_enabled': '0',
            })
            module._blank = False
            return module
        raise GDOException(t('err_module', (html(name),)))

    def __init__(self):
        self._cache = {}
        self._enabled = []
        self._methods = {}

    def get_module(self, module_name: str) -> 'GDO_Module':
        return self._cache.get(module_name, None)

    def get_method(self, method_trigger: str) -> Method | None:
        try:
            method = self._methods[method_trigger.lower()]
            fqn = method.get_fqn()
            module_name, class_name = fqn.rsplit('.', 1)
            module = importlib.import_module(module_name)
            class_object = getattr(module, class_name)
            return class_object()
        except Exception:
            return None

    def sort_cache(self):
        cc = sorted(self._cache.items(), key=lambda mod: mod[1]._priority)
        self._cache = {k: v for k, v in cc}
        return self

    def load_modules_fs(self, pattern='*', installed=False):
        loaded = {}
        patterns = pattern.split(',')
        for pattern in patterns:
            path = Application.file_path('gdo/')
            matches = glob.glob(pattern, root_dir=path)
            if not matches:
                print(f"Pattern {pattern} does not match any module.", file=sys.stderr)
            for dirname in matches:
                if not dirname.startswith('_'):
                    if Files.is_dir(path + dirname):
                        if module := self.load_module_fs(dirname, installed):
                            loaded[dirname] = module
        self.sort_cache()
        return loaded

    def load_module_fs(self, modulename, installed=False):
        if module := self._cache.get(modulename):
            module = self._cache[modulename]
            if installed and not module.installed():
                return None
            return module
        if installed and not self.module_installed(modulename):
            return None
        module = self.gdo_import(modulename)
        if not module:
            raise GDOException(f"Cannot import module {modulename}")
        return module

    def module_installed(self, modulename: str) -> bool:
        from gdo.base.GDO_Module import GDO_Module
        try:
            if GDO_Module.table().get_by_name(modulename, True):
                return True
        except GDODBException:
            pass
        return False

    def on_module_installed(self, module: 'GDO_Module'):
        self._cache[module.get_name()] = module
        module.init()

    def after_delete(self, module: GDO_Module):
        if module.get_name() in self._cache:
            del self._cache[module.get_name()]

    def load_modules_db(self, enabled: None | bool = True):
        from gdo.base.GDO_Module import GDO_Module
        back = []
        query = GDO_Module.table().select()
        if isinstance(enabled, bool):
            query.where(f"module_enabled=%i" % enabled)
        result = query.order('module_priority').exec()
        for db in result:
            try:
                fs = self.gdo_import(db.gdo_val('module_name'))
                fs._vals = db._vals
                back.append(fs.all_dirty(False))
            except Exception as ex:
                Logger.exception(ex)
        self._enabled = back
        return back

    def load_module_db(self, modulename, enabled=False):
        from gdo.base.GDO_Module import GDO_Module
        db = GDO_Module.table().get_by_name(modulename)
        fs = self.gdo_import(modulename)
        if db:
            fs.vals(db._vals)
        else:
            return None
        if enabled:
            if not fs.is_enabled():
                return None
        return fs

    def init_user_settings(self):
        from gdo.core.GDT_UserSetting import GDT_UserSetting
        from gdo.core.GDT_Field import GDT_Field
        for module in self._cache.values():
            for gdt in module.gdo_user_config():
                if isinstance(gdt, GDT_Field):
                    GDT_UserSetting.register(gdt)
            for gdt in module.gdo_user_settings():
                if isinstance(gdt, GDT_Field):
                    GDT_UserSetting.register(gdt)

    def init_modules(self, enabled: bool = True, load_vals: bool = False):
        if load_vals:
            self.load_module_vars()
            self.init_user_settings()
        from gdo.ui.GDT_Page import GDT_Page
        GDT_Page.clear_assets()
        for module in self._cache.values():
            if enabled and not module.is_enabled():
                continue
            module.init()
            module.gdo_load_scripts(GDT_Page())

    def reload_modules(self):
        self.init_modules(True, True)
        for module in self._cache.values():
            if not module.is_enabled():
                continue
            module._inited = False
            module.init()

    def load_module_vars(self):
        result = GDO_ModuleVal.table().select('module_name, mv_key, mv_val').join_object('mv_module').all().exec(False).iter(ResultType.ROW)
        for config in result:
            module_name, key, val = config
            if module := self.get_module(module_name):
                module.config_column(key).initial(val)

    def init_cli(self):
        """
        Init all methods
        """
        for module in self._cache.values():
            for method in module.get_methods():
                try:
                    if trigger := method.__class__.gdo_trigger():
                        self._methods[trigger.lower()] = method
                        if trig := method.__class__.gdo_trig():
                            if trig.lower() not in self._methods:
                                self._methods[trig.lower()] = method
                except Exception as ex:
                    Logger.exception(ex, f"Error in {method.__module__}.{method.__class__.__name__}")

    def get_module_method(self, module_name: str, method_name: str) -> Method:
        return self.get_module(module_name).get_method(method_name)

