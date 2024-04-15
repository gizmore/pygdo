import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import CLI


class CLITestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        ModuleLoader.instance().init_cli()
        return self

    def test_echo(self):
        result = CLI.parse("echo \"Hello world\"").execute().render_cli()
        self.assertIn('Hello world', result, 'Test if CLI core.echo "Hello world" works.')

        result = CLI.parse("echo Hello world").execute().render_cli()
        self.assertIn('Hello world', result, 'Test if CLI core.echo "Hello world" works.')



if __name__ == '__main__':
    unittest.main()
