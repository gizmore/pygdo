import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.base.Query import Query
from gdo.admin.method.users import users
from gdotest.TestUtil import GDOTestCase, install_module, web_gizmore, web_plug


class AdminUsersTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        install_module('admin')

    def test_joins_every_registered_user_setting(self):
        method = users()
        query = method.gdo_table_query()
        self.assertTrue(query._columns.startswith('gdo_user.*'))
        for key, field in GDT_UserSetting.KNOWN.items():
            if not isinstance(field, GDT_Field) or field.is_secret():
                self.assertNotIn(f'setting_{key}.uset_val as {key}', query._columns)
                continue
            self.assertIn(f'setting_{key}.uset_val as {key}', query._columns)

    def test_admin_permission_is_required(self):
        self.assertEqual('admin', users().gdo_user_permission())

    def test_paginates_fifty_users_per_page(self):
        self.assertEqual(50, users().gdo_paginate_size())

    def test_module_sort_is_writable_but_priority_stays_fixed(self):
        module = ModuleLoader.instance().get_module('admin')
        self.assertTrue(module.column('module_sort').is_writable())
        self.assertFalse(module.column('module_priority').is_writable())

    def test_module_configuration_url_keeps_the_module_parameter(self):
        web_gizmore()
        out = web_plug('admin.module.module.admin.html').user('gizmore').exec()
        self.assertNotIn('Invalid value for parameter module', out)
        self.assertIn('module_sort', out)

    def test_qualifies_the_default_order_column(self):
        self.assertEqual('gdo_user.user_id ASC', users().gdo_order_default())

    def test_has_a_non_sortable_edit_user_action_column(self):
        field = users().gdo_table_headers()[1]
        self.assertEqual('edit_user', field.get_name())
        self.assertFalse(field.is_filterable())
        self.assertFalse(field.is_orderable())

    def test_unset_settings_render_as_a_dash_but_stay_null_in_json(self):
        field = users().setting_fields()[0].val(None)
        self.assertEqual('---', field.render_cell())
        self.assertIsNone(field.render_json())

    def test_setting_filters_use_the_joined_setting_column(self):
        field = next(field for field in users().setting_fields() if field.get_name() == 'last_activity')
        query = Query().select().table('gdo_user')
        field.val({'date_from': '2026-08-26'}).gdo_filter_query(GDO_User.table(), query)
        self.assertIn("setting_last_activity.uset_val>='2026-08-26 00:00:00'", query._where)

    def test_object_setting_filters_do_not_join_a_nonexistent_user_column(self):
        field = next(field for field in users().setting_fields() if field.get_name() == 'creator')
        query = Query().select().table('gdo_user')
        field.val('giz').gdo_filter_query(GDO_User.table(), query)
        self.assertIn('setting_creator.uset_val IN (SELECT user_id FROM gdo_user', query._where)



if __name__ == '__main__':
    unittest.main()
