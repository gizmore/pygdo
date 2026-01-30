import unittest
import os
import subprocess

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import GDOTestCase, reinstall_module, cli_plug, install_module


class ConfigureTestCase(GDOTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules(True, True)
        ModuleLoader.instance().init_cli()
        Application.init_cli()

    async def test_01_configure(self):
        date1 = Application.CONFIG['gen']['date']
        result = subprocess.run(["python3", Application.file_path("gdoadm.py"), "-u", "configure"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Application.init(os.path.dirname(__file__) + "/../")
        date2 = Application.CONFIG['gen']['date']
        self.assertNotEqual(date1, date2, "Cannot rewrite config.")

    async def test_10_confc(self):
        cli_plug(None, '$confc echo dis 1')
        out = cli_plug(None, '$echo 1')
        self.assertIn('disabled here', out, 'confc does not work.')
        cli_plug(None, '$confc ech dis 0')
        out = cli_plug(None, '$echo 1')
        self.assertIn('1', out, 'confc#2 does not work.')

if __name__ == '__main__':
    unittest.main()
