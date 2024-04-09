import os.path
import unittest

from gdo.core.Application import Application
from gdotest.test_install import InstallTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(InstallTestCase())
    return suite


if __name__ == '__main__':
    Application.init(os.path.dirname(__file__))
    runner = unittest.TextTestRunner()
    runner.run(suite())
