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
from gdotest.test_core import CoreTestCase
from gdotest.test_date import DateTestCase
from gdotest.test_db import DBTestCase
from gdotest.test_dog import DogTestCase
from gdotest.test_events import EventsTestCase
from gdotest.test_finish import FinishTestCase
from gdotest.test_forms import FormTestCase
from gdotest.test_install import InstallTestCase
from gdotest.test_mail import MailTestCase
from gdotest.test_math import MathTestCase
from gdotest.test_module_config import ModuleConfigTestCase
from gdotest.test_session import SessionTestCase
from gdotest.test_ui import UITestCase
from gdotest.test_users import UsersTestCase
from gdotest.test_util import UtilityTestCase
from gdotest.test_web import WebTestCase


def suite():
    mysuite = unittest.TestSuite()
    unittest.TestLoader.sortTestMethodsUsing = None
    loader = unittest.TestLoader()
    mysuite.addTests(loader.loadTestsFromTestCase(InstallTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(ConfigureTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(ModuleConfigTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(CoreTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DateTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(MathTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DBTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(FormTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(EventsTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(UITestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(UtilityTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(CLITestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(UsersTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(SessionTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(WebTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(MailTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DogTestCase))
    return mysuite


def finisher():
    mysuite = unittest.TestSuite()
    unittest.TestLoader.sortTestMethodsUsing = None
    loader = unittest.TestLoader()
    mysuite.addTests(loader.loadTestsFromTestCase(FinishTestCase))
    return mysuite


def run_tests():
    Application.init(os.path.dirname(__file__) + '/')

    # Core
    test_runner = unittest.TextTestRunner()
    test_runner.verbosity = 3
    test_runner.run(suite())

    # Extensions
    loader = ModuleLoader.instance()
    modules = list(loader.load_modules_fs().values())
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

    # Finish
    test_runner = unittest.TextTestRunner()
    test_runner.verbosity = 3
    test_runner.run(finisher())


if __name__ == '__main__':
    run_tests()
