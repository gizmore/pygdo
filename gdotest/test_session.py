import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Parser import Parser
from gdo.base.Util import CLI
from gdo.base.ModuleLoader import ModuleLoader


class SessionTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()
        loader.init_cli()
        return self

    def test_cli_session(self):
        user = CLI.get_current_user()
        method = Parser("echo hi", user).parse()
        result = method.execute().render_cli()
        self.assertIn('hi', result, 'echo does not work for session test.')
        session = method._session.set('tea', 'hot')
        sat = 'hot'
        got = session.get('tea')
        session.save()
        self.assertEqual(sat, got, 'session does not work instantly')
        # a second process
        method = Parser("echo hi", user).parse()
        result = method.execute().render_cli()
        self.assertIn('hi', result, 'echo does not work for session test2.')
        got = method._session.get('tea')
        self.assertEqual(sat, got, 'session does not work across processes')


if __name__ == '__main__':
    unittest.main()
