import os
from gdo.core.Application import Application
from gdo.core.ModuleLoader import ModuleLoader
from gdo.install.Installer import Installer


def init():
    Application.init(os.path.dirname(__file__))
    ModuleLoader.instance().load_modules_fs('')
    Installer.install_modules(ModuleLoader.instance().sort_cache()._cache.values())


if __name__ == "__main__":
    init()
