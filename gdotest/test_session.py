import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Parser import Parser
from gdo.base.Util import CLI
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import cli_plug


class SessionTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()
        loader.init_cli()
        return self

    def test_cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        user = CLI.get_current_user()
        result = cli_plug(user, "$echo hi")
        self.assertIn('hi', result, 'echo does not work for session test.')
        session = GDO_Session.for_user(user).set('tea', 'hot')
        sat = 'hot'
        got = session.get('tea')
        session.save()
        self.assertEqual(sat, got, 'session does not work instantly')
        # a second process
        result = cli_plug(user, "$echo hi")
        self.assertIn('hi', result, 'echo does not work for session test2.')
        Application.fresh_page()
        session = GDO_Session.for_user(user)
        got = session.get('tea')
        self.assertEqual(sat, got, 'session does not work across processes')


if __name__ == '__main__':
    unittest.main()
