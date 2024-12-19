import asyncio
import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + '/../')
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()

    def test_web_user(self):
        gizmore = asyncio.run(Web.get_server().get_or_create_user('gizmore'))
        self.assertIsInstance(gizmore, GDO_User, "Cannot create gizmore for webserver")


if __name__ == '__main__':
    unittest.main()
