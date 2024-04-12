import os.path
import subprocess
import unittest

from gdo.core import module_core
from gdo.base.Application import Application
from gdo.base.Exceptions import GDODBException
from gdo.base.GDO_Module import GDO_Module
from gdo.base.ModuleLoader import ModuleLoader
from gdo.user.GDO_User import GDO_User


class InstallTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        return self

    def test_core_install(self):
        db = Application.DB
        self.assertTrue(db.is_configured(), 'Database is configured')
        self.assertIsNotNone(db.get_link(), 'Database is ready')

        loader = ModuleLoader.instance()
        modules = loader.load_modules_fs()
        self.assertGreater(len(modules), 5, 'Some modules can be loaded')

        subprocess.run(["python", "gdoadm.py", "wipe", "--all"], capture_output=True)
        with self.assertRaises(GDODBException, msg="Test if all modules are deleted"):
            GDO_Module.table().count_where()

        subprocess.run(["/bin/python3", "gdoadm.py", "install", "--module", "Core"], capture_output=True)
        mc_one = GDO_Module.table().count_where()
        need = len(module_core.instance().gdo_dependencies())
        self.assertGreater(mc_one, need, "Test if core module is installed with dependencies")

        subprocess.run(["/bin/python3", "gdoadm.py", "install", "--module", "Core"], capture_output=True)
        mc_two = GDO_Module.table().count_where()
        self.assertEqual(mc_one, mc_two, "Test if no more modules are installed on a second run")

    def test_loading_of_modules(self):
        loader = ModuleLoader.instance()
        mods = loader.load_modules_db(False)
        self.assertEqual(len(mods), 0, 'Test if loading uninstalled modules from db somewhat works')

    def test_system_created(self):
        self.assertIsInstance(GDO_User.system(), GDO_User, 'Test if system user exists')
        self.assertEqual(GDO_User.system().get_id(), '1', 'Test if system user has ID#1')




if __name__ == '__main__':
    unittest.main()
