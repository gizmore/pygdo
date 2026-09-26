import hashlib
import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.base.Database import Database


class DatabaseTest(GDOTestCase):

    def test_constraint_name_keeps_short_names_readable(self):
        self.assertEqual(
            'GDO__FK__gdo_user__user_language',
            Database.constraint_name('FK', 'gdo_user', 'user_language'),
        )

    def test_constraint_name_hashes_only_an_overlong_tail(self):
        table = 'gdo_oraclesubscription_with_an_even_longer_suffix'
        column = 'unique_oracle_channel_with_an_even_longer_suffix'
        original = f'GDO__UNIQUE__{table}__{column}'
        name = Database.constraint_name('UNIQUE', table, column)
        self.assertEqual(64, len(name))
        self.assertTrue(name.startswith(original[:30] + '__'))
        self.assertTrue(name.endswith(hashlib.md5(original.encode()).hexdigest()))


if __name__ == '__main__':
    unittest.main()
