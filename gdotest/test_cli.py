import os.path
import subprocess
import unittest

from bin.pygdo import run
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import CLI
from gdo.base import module_base
from gdotest.TestUtil import cli_plug


class CLITestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        ModuleLoader.instance().init_cli()
        return self

    def test_01_echo(self):
        result = CLI.parse("echo \"Hello world\"").execute().render_cli()
        self.assertIn('Hello world', result, 'Test if CLI core.echo "Hello world" works.')
        result = CLI.parse("echo Hello world").execute().render_cli()
        self.assertIn('Hello world', result, 'Test if CLI core.echo "Hello world" works.')

    def test_02_version(self):
        result = CLI.parse("core.version").execute().render_cli()
        self.assertIn(str(module_base.instance().CORE_VERSION), result, 'Test if CLI version contains version number.')
        self.assertIn('GDO', result, 'Test if CLI version contains version number.')
        self.assertIn('Python', result, 'Test if CLI version contains version number.')

    def test_03_binary(self):
        result = subprocess.run(["pygdo", "echo", "Hello world"], capture_output=True)
        self.assertIn('Hello world', str(result.stdout), 'Test if CLI core.echo "Hello world" works via binary execution.')

    def test_04_perf(self):
        result = cli_plug(None, "core.perf")
        self.assertIn('Memory', result, 'Test if CLI core.perf renders ok.')

    def test_05_help_overview(self):
        result = cli_plug(None, "help")




if __name__ == '__main__':
    unittest.main()
