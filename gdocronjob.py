import sys

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.Cronjob import Cronjob


if __name__ == '__main__':
    Application.init(__file__ + "/../")
    loader = ModuleLoader.instance()
    loader.load_modules_db()
    loader.init_modules(True, True)
    Cronjob.run('--force' in sys.argv)
