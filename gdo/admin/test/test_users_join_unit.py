import unittest
from unittest.mock import MagicMock, patch

from gdo.admin.method.users import users
from gdo.base.Application import Application
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.base.ModuleLoader import ModuleLoader
from gdo.table.MethodQueryTable import MethodQueryTable


class UsersJoinUnitTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_html)

    def test_many_settings_use_one_join_and_quote_reserved_alias(self):
        method = users()
        names = ['ignore'] + [f'field_{i}' for i in range(80)]
        fields = [MagicMock(get_name=MagicMock(return_value=name)) for name in names]
        query = Query().select().table('gdo_user')
        with patch.object(MethodQueryTable, 'gdo_table_query', return_value=query), \
             patch.object(users, 'setting_fields', return_value=fields):
            result = method.gdo_table_query()
        self.assertEqual(1, result._join.count('JOIN'))
        self.assertIn('user_settings.`ignore` AS `ignore`', result._columns)
        self.assertIn("CASE WHEN uset_key='field_79'", result._join)
        self.assertIn('GROUP BY uset_user', result._join)

    def test_no_settings_needs_no_join(self):
        method = users()
        query = Query().select().table('gdo_user')
        with patch.object(MethodQueryTable, 'gdo_table_query', return_value=query), \
             patch.object(users, 'setting_fields', return_value=[]):
            method.gdo_table_query()
        self.assertEqual('', query._join)

    def test_filter_uses_projected_setting_column(self):
        template = GDT_String('sample')
        with patch.object(ModuleLoader, 'instance') as loader, \
             patch.dict(GDT_UserSetting.KNOWN, {'sample': template}, clear=True):
            loader.return_value.init_user_settings.return_value = None
            field = users().setting_fields()[0]
            query = Query().select().table('gdo_user')
            field.val('hello').gdo_filter_query(MagicMock(), query)
        self.assertIn('user_settings.`sample`', query._where)
        self.assertIn('hello', query._where)
