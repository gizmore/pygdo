from __future__ import annotations

import sys

from typing_extensions import Self

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.base.GDO_Module import GDO_Module

import glob
import importlib

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOException, GDODBException
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.Method import Method
from gdo.base.Result import ResultType
from gdo.base.Util import Files


class ModuleLoader:
    _cache: dict[str, 'GDO_Module']
    _methods: dict[str, any]
    _enabled: []

    @classmethod
    def instance(cls) -> Self:
        return Application.LOADER

    def enabled(self) -> list[GDO_Module]:
        yield from self._enabled

    def reset(self):
        self._cache.clear()

    def gdo_import(self, name: str) -> 'GDO_Module':
        mn = importlib.import_module("gdo." + name)
        classname = 'module_' + name
        if klass := mn.__dict__.get(classname):
            self._cache[name] = module = klass.blank({
                'module_name': name,
                'module_enabled': '0',
            })
            return module

    def __init__(self):
        self._cache = self.__dict__.get('_cache', {})

    def get_module(self, module_name: str) -> 'GDO_Module':
        return self._cache.get(module_name, None)

    def get_method(self, method_trigger: str) -> Method | None:
        try:
            method = self._methods[method_trigger.lower()]
            fqn = method.fqn()
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
        if modulename in self._cache.keys():
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
            fs = self.gdo_import(db.gdo_val('module_name'))
            fs._vals = db._vals
            back.append(fs.all_dirty(False))
        self._enabled = back
        return back

    def load_module_db(self, modulename, enabled=False):
        from gdo.base.GDO_Module import GDO_Module
        db = GDO_Module.table().get_by_name(modulename)
        fs = self.gdo_import(modulename)
        if db:
            fs._vals.update(db._vals)
            fs.all_dirty(False)
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
        for module in self._cache.values():
            if enabled and not module.is_enabled():
                continue
            module.init()

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
            self.get_module(module_name).config_column(key).initial(val)

    def init_cli(self):
        """
        Init all methods
        """
        self._methods = {}
        for module in self._cache.values():
            for method in module.get_methods():
                if trigger := method.gdo_trigger():
                    self._methods[trigger.lower()] = method
