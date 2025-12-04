import unittest

from gdotest.test_admin import AdminTestCase
from gdotest.test_cli import CLITestCase
from gdotest.test_configure import ConfigureTestCase
from gdotest.test_core import CoreTestCase
from gdotest.test_date import DateTestCase
from gdotest.test_db import DBTestCase
from gdotest.test_dog import DogTestCase
from gdotest.test_events import EventsTestCase
from gdotest.test_finish import FinishTestCase
from gdotest.test_forms import FormTestCase
from gdotest.test_gdopack import GDOPackTestCase
from gdotest.test_install import InstallTestCase
from gdotest.test_mail import MailTestCase
from gdotest.test_math import MathTestCase
from gdotest.test_message import MessageTestCase
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
    mysuite.addTests(loader.loadTestsFromTestCase(CoreTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(GDOPackTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(ModuleConfigTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(AdminTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(DateTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(MathTestCase))
    mysuite.addTests(loader.loadTestsFromTestCase(MessageTestCase))
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
    mysuite.addTests(loader.loadTestsFromTestCase(FinishTestCase))
    return mysuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.verbosity = 4
    # with yappi.run():
    runner.run(suite())
    # yappi.stop()
    # yappi.get_func_stats().print_all()

