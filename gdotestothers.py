import os.path
import unittest

import gdotest
from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Files
from gdo.install.Installer import Installer


def run_tests():
    Application.init(os.path.dirname(__file__) + '/')

    loader = ModuleLoader.instance()
    modules = list(loader.load_modules_fs().values())
    loader.init_modules()
    Installer.install_modules(modules)
    for module in modules:
        test_directory = module.file_path('test/')
        if Files.exists(test_directory):
            Logger.debug(f"Running tests for {module.get_name()}")
            test_loader = unittest.TestLoader()
            test_suite = test_loader.discover(test_directory, pattern='test_*.py')
            test_runner = unittest.TextTestRunner()
            test_runner.verbosity = 3
            test_runner.run(test_suite)


if __name__ == '__main__':
    run_tests()
