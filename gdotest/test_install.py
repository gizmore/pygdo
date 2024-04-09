import os.path
import subprocess
import unittest

from gdo.core import module_core
from gdo.core.Application import Application
from gdo.core.Exceptions import GDODBException
from gdo.core.GDO_Module import GDO_Module
from gdo.core.ModuleLoader import ModuleLoader


class InstallTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        return self

    def runTest(self):
        db = Application.DB
        self.assertTrue(db.is_configured(), 'Database is configured')
        self.assertIsNotNone(db.get_link(), 'Database is ready')

        loader = ModuleLoader.instance()
        modules = loader.load_modules_fs()
        self.assertGreater(len(modules), 5, 'Some modules can be loaded')

        result = subprocess.run(["python", "gdoadm.py", "wipe", "--all"], capture_output=True)
        self.assertRaises(GDODBException, GDO_Module.table().count_where, "Test if all modules are deleted")

        result = subprocess.run(["/bin/python3", "gdoadm.py", "install", "--module", "Core"], capture_output=True)
        mc = GDO_Module.table().count_where()
        self.assertGreater(mc, len(module_core.instance().gdo_dependencies()), "Test if core module is installed with dependencies")
