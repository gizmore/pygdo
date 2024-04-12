import os
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader


def init():
    Application.init(os.path.dirname(__file__))
    ModuleLoader.instance().load_modules_cached()



if __name__ == "__main__":
    init()
