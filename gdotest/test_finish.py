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
        self.assertEqual(len(Trans.FAILURES), 0, 'There are Translation errors left.')


if __name__ == '__main__':
    unittest.main()
