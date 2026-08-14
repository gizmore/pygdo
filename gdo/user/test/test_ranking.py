import os
import unittest
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.user.module_user import module_user
from gdotest.TestUtil import GDOTestCase, install_module, web_gizmore, web_plug


class UserRankingTest(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        install_module('user')
        loader.load_modules_db()
        loader.init_modules(True, True)
        Application.init_cli()

    def test_ranking_renders_profile_link(self):
        Application.set_session(GDO_Session.for_user(web_gizmore()))
        out = web_plug('user.ranking.html').exec()
        self.assertIn('gizmore', out)
        self.assertIn('/user.profile.for.', out)
        self.assertIn('name="s"', out)
        self.assertIn('name="f[user_name]"', out)
        self.assertIn('o=user_name%20ASC', out)
        self.assertIn('o=level%20DESC', out)
        out = web_plug('user.ranking.f%5Buser_name%5D.gizmore.html').exec()
        self.assertIn('gizmore', out)
        self.assertNotIn('chappy', out)

        out = web_plug('user.ranking.f%5Buser_server%5D.netcat.html').exec()
        self.assertIn('netcat', out)
        self.assertNotIn('>9-wechall</td>', out)

    def test_ghost_never_gets_a_last_activity_setting(self):
        with patch.object(GDO_User, 'save_setting') as save_setting:
            module_user.instance().set_last_activity(GDO_User.ghost())
        save_setting.assert_not_called()


if __name__ == '__main__':
    unittest.main()
