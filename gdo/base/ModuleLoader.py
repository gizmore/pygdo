from __future__ import annotations

import glob
import importlib
import os

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOException


class ModuleLoader:
    _instance = None
    _cache: dict

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = ModuleLoader()
        return cls._instance

    def gdo_import(self, name):
        # Logger.debug(f'gdo_import({name})')
        mn = importlib.import_module("gdo." + name)
        classname = 'module_' + name
        if classname in mn.__dict__.keys():
            self._cache[name] = mn.__dict__[classname]()
            return self._cache[name]
        return None

    def __init__(self):
        self._cache = {}

    def get_module(self, module_name):
        return self._cache[module_name]

    def sort_cache(self):
        cc = sorted(self._cache.items(), key=lambda mod: mod[1]._priority)
        self._cache = {k: v for k, v in cc}
        return self

    def load_modules_fs(self, pattern='*', installed=False):
        path = Application.file_path('gdo/')
        for dirname in glob.glob(pattern, root_dir=path):
            if os.path.isdir(path + dirname):
                if not dirname.startswith('_'):
                    self.load_module_fs(dirname, installed)
        return self._cache

    def load_module_fs(self, modulename, installed=False):
        if modulename in self._cache.keys():
            module = self._cache[modulename]
            if installed:
                if not module.installed():
                    return None
            return module
        if installed:
            if not self.module_installed(modulename):
                return None
        return self.gdo_import(modulename)

    def module_installed(self, modulename: str) -> bool:
        from gdo.base.GDO_Module import GDO_Module
        if not Application.DB.is_configured():
            raise GDOException("Database not configured!")
        if GDO_Module.table().get_by_name(modulename, True):
            return True
        return False

    def load_modules_db(self, enabled: None | bool):
        from gdo.base.GDO_Module import GDO_Module
        back = []
        query = GDO_Module.table().select()
        if isinstance(enabled, bool):
            query.where(f"module_enabled=%i" % enabled)
        result = query.exec()
        for db in result:
            fs = self.gdo_import(db.gdo_val('module_name'))
            fs.set_vals(db._vals, False)
            fs.all_dirty(False)
            back.append(fs)
        return back

    def load_module_db(self, modulename, enabled=False):
        from gdo.base.GDO_Module import GDO_Module
        db = GDO_Module.table().get_by_name(modulename)
        fs = self.gdo_import(modulename)
        if db:
            fs.set_vals(db._vals)
        else:
            return None
        if enabled:
            if not fs.is_enabled():
                return None
        return fs

    def init_modules(self, enabled=True):
        for module in self._cache.values():
            if enabled and module.is_enabled():
                module.init_language()
        for module in self._cache.values():
            if enabled and module.is_enabled():
                module.gdo_init()

    def load_modules_cached(self):
        return self.load_modules_db(True)

