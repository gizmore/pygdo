import unittest

from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web


class UsersTestCase(unittest.TestCase):

    def test_web_user(self):
        gizmore = Web.get_server().get_or_create_user('gizmore')
        self.assertIsInstance(gizmore, GDO_User, "Cannot create gizmore for webserver")


if __name__ == '__main__':
    unittest.main()
