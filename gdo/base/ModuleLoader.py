from __future__ import annotations

import glob
import importlib

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOException, GDODBException
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.Method import Method
from gdo.base.Result import ResultType
from gdo.base.Util import Files


class ModuleLoader:
    _cache: dict[str, any]
    _methods: dict[str, any]

    @classmethod
    def instance(cls):
        return Application.LOADER

    def enabled(self):
        for module in self._cache.values():
            if module.is_enabled():
                yield module

    def reset(self):
        self._cache = {}

    def gdo_import(self, name):
        mn = importlib.import_module("gdo." + name)
        classname = 'module_' + name
        if classname in mn.__dict__.keys():
            self._cache[name] = module = mn.__dict__[classname]()
            module.init_language()
            return module
        return None

    def __init__(self):
        self._cache = self.__dict__.get('_cache', {})

    def get_module(self, module_name):
        return self._cache[module_name]

    def get_method(self, method_trigger: str) -> Method | None:
        try:
            method = self._methods[method_trigger]
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
            for dirname in glob.glob(pattern, root_dir=path):
                if not dirname.startswith('_'):
                    if Files.is_dir(path + dirname):
                        loaded[dirname] = self.load_module_fs(dirname, installed)
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

    def load_modules_db(self, enabled: None | bool = True):
        from gdo.base.GDO_Module import GDO_Module
        back = []
        query = GDO_Module.table().select()
        if isinstance(enabled, bool):
            query.where(f"module_enabled=%i" % enabled)
        result = query.exec()
        for db in result:
            fs = self.gdo_import(db.gdo_val('module_name'))
            fs._vals.update(db._vals)
            fs.all_dirty(False)
            back.append(fs)
        return back

    def load_module_db(self, modulename, enabled=False):
        from gdo.base.GDO_Module import GDO_Module
        db = GDO_Module.table().get_by_name(modulename)
        fs = self.gdo_import(modulename)
        if db:
            fs._vals.update(db._vals)
            fs.all_dirty(False)
            fs._is_persisted = True
        else:
            return None
        fs.init_language()
        if enabled:
            if not fs.is_enabled():
                return None
        return fs

    def init_user_settings(self):
        from gdo.core.GDT_UserSetting import GDT_UserSetting
        for module in self._cache.values():
            for gdt in module.gdo_user_config():
                GDT_UserSetting.register(gdt)
            for gdt in module.gdo_user_settings():
                GDT_UserSetting.register(gdt)

    def init_modules(self, enabled: bool = True):
        self.init_user_settings()
        for module in self._cache.values():
            if enabled and not module.is_enabled():
                continue
            module.init()

    def load_module_vars(self):
        result = GDO_ModuleVal.table().select('module_name, mv_key, mv_val').join_object('mv_module').all().exec().iter(ResultType.ROW)
        for config in result:
            module_name, key, val = config
            self.get_module(module_name).config_column(key).initial(val)

    def load_modules_cached(self):
        return self.load_modules_db(True)

    def init_cli(self):
        """
        Init all methods
        """
        self._methods = {}
        for module in self._cache.values():
            for method in module.get_methods():
                trigger = method.gdo_trigger()
                if trigger:
                    self._methods[trigger] = method


