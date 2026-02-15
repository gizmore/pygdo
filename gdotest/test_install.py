import os.path
import subprocess
import unittest

from gdo.core import module_core
from gdo.base.Application import Application
from gdo.base.Exceptions import GDODBException
from gdo.base.GDO_Module import GDO_Module
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.method.clear_cache import clear_cache
from gdo.install.Installer import Installer
from gdotest.TestUtil import reinstall_module, GDOTestCase, web_plug


class InstallTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()

    async def test_01_core_config(self):
        db = Application.db()
        self.assertTrue(db.is_configured(), 'Database is configured')
        self.assertIsNotNone(db.get_link(), 'Database is ready')

    async def test_01b_all_modules_have_nice_deps(self):
        loader = ModuleLoader.instance()
        modules = loader.load_modules_fs()
        tested = 0
        for name, module in modules.items():
            deps = module.gdo_dependencies()
            for dep in deps:
                self.assertIsInstance(dep, str, f"{name} has incorrect deps")
                self.assertIsInstance(loader.get_module(name), GDO_Module, f"{name} dependency {dep} is not a module.")
                tested += 1
        self.assertGreater(tested, 5, "Does not have much dependencies tested!")

    async def test_01c_installer_resolves_all_dependencies(self):
        loader = ModuleLoader.instance()
        modules = loader.load_modules_fs()
        with_deps = Installer.modules_with_deps(list(modules.values()))
        self.assertEqual(len(modules), len(with_deps), "Something is fishy in module deps!")

    async def test_02_wipe(self):
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), '-u', 'wipe', "--all"], capture_output=True)
        with self.assertRaises(GDODBException, msg="Test if all modules are deleted"):
            GDO_Module.table().count_where()

    async def test_03_core_install(self):
        loader = ModuleLoader.instance()
        modules = loader.load_modules_fs()
        loader.init_modules()
        self.assertGreater(len(modules), 5, 'Some modules can be loaded')

        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), "-u", "install", "Core"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mc_one = GDO_Module.table().count_where()
        need = len(module_core.instance().gdo_dependencies())
        if mc_one < need:
            print(result.stderr)
            print(result.stdout)
        self.assertGreater(mc_one, need, "Test if core module is installed with dependencies")

        subprocess.run(["python3", Application.file_path("gdoadm.py"), "-u", "install", "Core"], capture_output=True)
        mc_two = GDO_Module.table().count_where()
        self.assertEqual(mc_one, mc_two, "Test if no more modules are installed on a second run")

    async def test_04_loading_of_modules(self):
        loader = ModuleLoader.instance()
        mods = loader.load_modules_db(False)
        self.assertEqual(len(mods), 0, 'Test if loading uninstalled modules from db somewhat works')

    async def test_05_system_created(self):
        self.assertIsInstance(GDO_User.system(), GDO_User, 'Test if system user exists')
        self.assertEqual(GDO_User.system().get_id(), '1', 'Test if system user has ID#1')

    async def test_06_install_single_modules(self):
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), '-u', 'install', "date"], capture_output=True)
        self.assertIn('All Done!', result.stdout.decode('UTF-8'), "Install one single module")
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), '-u', 'install', "ma*,date"], capture_output=True)
        self.assertIn('All Done!', result.stdout.decode('UTF-8'), "Install some modules")

    async def test_07_install_all_modules(self):
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), '-u', 'install', "--all"], capture_output=True)
        self.assertIsNotNone(result, "Install all")

    async def test_08_install_admin_user(self):
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), '-u', 'admin', "gizmore5", "11111111", "gizmore@gizmore.org"], capture_output=True)
        self.assertTrue(GDO_User.table().get_by_vals({'user_name': 'gizmore5', 'user_server': '1'}).is_admin(), 'Cannot create admin user')

    def test_09_reinstall_module(self):
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()
        web_plug('/core.welcome.html?_lang=en').user('gizmore').exec()
        out = web_plug('/core.welcome.html?_lang=en').user('gizmore').exec()
        self.assertIn('Welcome', out, 'web request no work.')
        reinstall_module('login')
        self.assertIn('login', ModuleLoader.instance()._cache, 'Cannot reinstall modules.')


if __name__ == '__main__':
    unittest.main()
