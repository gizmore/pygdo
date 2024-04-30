import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import Trans


class FinishTestCase(unittest.TestCase):
    """
    Check overall stats and errors as last test suite
    """

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()

    def test_01_no_translation_errors(self):
        count = len(Trans.FAILURES)
        missing = ', '.join(Trans.FAILURES.keys())
        self.assertEqual(count, 0, f'There are Translation errors left: {missing}.')


if __name__ == '__main__':
    unittest.main()
