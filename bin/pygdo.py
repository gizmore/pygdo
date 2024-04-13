import os
import sys

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import CLI

if __name__ == '__main__':
    Application.init(os.path.dirname(__file__))
    ModuleLoader.instance().load_modules_cached()
    method = CLI.parse(" ".join(sys.argv))
    print(method.execute().render())
