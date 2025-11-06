import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Util import CLI
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import cli_plug, GDOTestCase


class SessionTestCase(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        loader.init_cli()

    def test_cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        Cache.clear()
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
