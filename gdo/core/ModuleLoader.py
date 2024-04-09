import glob
import importlib
import os

from gdo.core.Application import Application
from gdo.core.Exceptions import GDODBException


class ModuleLoader:
    _instance = None
    _cache: dict

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = ModuleLoader()
        return cls._instance

    def gdo_import(self, name):
        mn = importlib.import_module("gdo." + name)
        classname = "module_" + name
        if classname in mn.__dict__.keys():
            self._cache[name] = mn.__dict__[classname]()
            return True
        return False

    def __init__(self):
        self._cache = {}

    def get_module(self, module_name):
        return self._cache[module_name]

    def sort_cache(self):
        cc = sorted(self.cache.items(), key=lambda mod: mod[1]._priority)
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
        if not Application.DB.is_configured():
            raise GDODBException("Database not configured!")
        return False

    # def module_instance(self, name):
    #     mn = "module_" + name
    #     return mn()
