import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User


class DBTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_01_single_identity_cache(self):
        user1 = GDO_User.system()
        user2 = GDO_User.table().select().where('user_id=1').first().exec().fetch_object()
        self.assertIs(user1, user2, "test if single identity cache works")


if __name__ == '__main__':
    unittest.main()
