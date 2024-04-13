import unittest

from gdotest.test_cli import CLITestCase
from gdotest.test_date import DateTestCase
from gdotest.test_db import DBTestCase
from gdotest.test_forms import FormTestCase
from gdotest.test_install import InstallTestCase
from gdotest.test_ui import UITestCase
from gdotest.test_util import UtilityTestCase


def suite():
    mysuite = unittest.TestSuite()
    loader = unittest.TestLoader()
    mysuite.addTests(loader.loadTestsFromTestCase(InstallTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DateTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DBTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(FormTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(UITestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(UtilityTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(CLITestCase))
    return mysuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

