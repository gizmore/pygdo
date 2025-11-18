import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base import module_base
from gdotest.TestUtil import cli_plug, GDOTestCase


class CLITestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules(True, True)
        ModuleLoader.instance().init_cli()
        Application.init_cli()

    async def test_01_echo(self):
        result = cli_plug(None, "$echo \\\"Hello world\\\"")
        self.assertEqual('"Hello world"', result, 'Test if CLI core.echo "Hello world" works.')
        result = cli_plug(None, "$echo \"Hello world\"")
        self.assertEqual('Hello world', result, 'Test if CLI core.echo "Hello world" works.')
        result = cli_plug(None, "$echo Hello world")
        self.assertEqual('Hello world', result, 'Test if CLI core.echo Hello world works.')

    async def test_02_version(self):
        result = cli_plug(None, "$version")
        self.assertIn(str(module_base.instance().CORE_VERSION), result, 'Test if CLI version contains version number.')
        self.assertIn('GDO', result, 'Test if CLI version contains version number.')
        self.assertIn('Python', result, 'Test if CLI version contains version number.')

    # async def test_03_binary(self):
    #     result = subprocess.run(["pygdo", "\\$echo", "Hello world"], capture_output=True)
    #     self.assertIn('Hello world', str(result.stdout), 'Test if CLI core.echo "Hello world" works via binary execution.')

    # async def test_04_perf(self):
    #     result = cli_plug(None, "$perf")
    #     self.assertIn('Memory', result, 'Test if CLI core.perf renders ok.')

    async def test_05_help_overview(self):
        result = cli_plug(None, "$help")
        self.assertIn("Core", result, "Help does not contain Core commands.")

    async def test_06_help_single_command(self):
        result = cli_plug(None, "$help version")
        self.assertIn("version", result, "Help does not contain Core commands.")
        result = cli_plug(None, "$help add_server")
        self.assertNotIn('--connector', result, "Help has problems with notnull parameters.")

    async def test_07_nested_command(self):
        line = "$echo 1 $(echo 2) $(echo 3 $(echo 4)) 5 $(echo 6) $(echo 7 8)"
        result = cli_plug(None, line)
        self.assertEqual('1 2 3 4 5 6 7 8', result, "Command nesting does not work.")


if __name__ == '__main__':
    unittest.main()
