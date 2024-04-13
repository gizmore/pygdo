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
        return self

    def test_echo(self):
        result = CLI.parse("core.echo 'Hello world'").execute().render_cli()
        self.assertEqual(result, 'Hello world', 'Test if CLI core.echo "Hello world" works.')

        result = CLI.parse("core.echo Hello world").render_cli()
        self.assertEqual(result, 'Hello world', 'Test if CLI core.echo "Hello world" works without quotes.')



if __name__ == '__main__':
    unittest.main()
