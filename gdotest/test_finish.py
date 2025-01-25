import os
import unittest

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import Trans
from gdotest.TestUtil import GDOTestCase


class FinishTestCase(GDOTestCase):
    """
    Check overall stats and errors as last test suite
    """

    def check_slots(self, obj: object):
        if hasattr(obj, '__slots__'):
            try:
                obj.foo = 1337
                self.assertTrue(False, f"{obj.__class__} has broken slots.")
            except:
                pass

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    def test_01_slots(self):
        classes = [
            Method,
        ]
        for klass in classes:
            self.check_slots(klass())
        for module in ModuleLoader.instance().enabled():
            for klass in module.gdo_classes():
                gdo = klass.blank()
                self.check_slots(gdo)

    # def test_01_no_translation_errors(self):
    #     count = len(Trans.FAILURES)
    #     missing = ', '.join(Trans.FAILURES.keys())
    #     self.assertEqual(count, 0, f'There are Translation errors left: {missing}.')


if __name__ == '__main__':
    unittest.main()
