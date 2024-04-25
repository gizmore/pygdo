import os.path
import unittest

import gdotest
from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Files
from gdo.install.Installer import Installer
from gdotest.test_cli import CLITestCase
from gdotest.test_configure import ConfigureTestCase
from gdotest.test_date import DateTestCase
from gdotest.test_db import DBTestCase
from gdotest.test_forms import FormTestCase
from gdotest.test_install import InstallTestCase
from gdotest.test_module_config import ModuleConfigTestCase
from gdotest.test_session import SessionTestCase
from gdotest.test_ui import UITestCase
from gdotest.test_users import UsersTestCase
from gdotest.test_util import UtilityTestCase
from gdotest.test_web import WebTestCase


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