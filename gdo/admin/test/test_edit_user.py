import os
import unittest

from gdo.admin.method.edit_user import edit_user
from gdo.admin.module_admin import module_admin
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Password import GDT_Password
from gdo.core.connector.Web import Web
from gdo.date.GDT_DateTime import GDT_DateTime
from gdo.ui.GDT_Divider import GDT_Divider
from gdo.ui.GDT_Link import GDT_Link
from gdotest.TestUtil import GDOTestCase, install_module


class EditUserTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        install_module('admin')
        Application.init_cli()
        loader.init_cli()
        self.target = await Web.get_server().get_or_create_user('admin_edit_user_target')
        self.staff = await Web.get_server().get_or_create_user('admin_edit_user_staff')
        self.staff._authenticated = True
        await GDO_UserPermission.grant(self.staff, 'staff')
        Application.set_current_user(self.staff)

    def method_for_target(self) -> edit_user:
        return (edit_user().env_user(self.staff, True).env_server(Web.get_server()).
                env_session(GDO_Session.for_user(self.staff)).env_mode(Mode.render_cli).
                input('user', str(self.target.get_id())))

    def test_staff_permission_and_user_picker(self):
        self.assertEqual('staff', edit_user().gdo_user_permission())
        form = edit_user().get_form()
        self.assertIsNotNone(form.get_field('select_user'))

    def test_every_registered_setting_is_editable_except_action_links(self):
        method = self.method_for_target()
        fields = {field.get_name(): field for field in method.setting_fields()}
        for key, template in GDT_UserSetting.KNOWN.items():
            if isinstance(template, GDT_Link):
                self.assertNotIn(key, fields)
            else:
                self.assertIn(key, fields)
                self.assertTrue(fields[key].is_writable())
                self.assertFalse(fields[key].is_hidden())

    def test_settings_are_grouped_by_module_dividers(self):
        form = self.method_for_target().get_form()
        dividers = [field for field in form.get_fields() if isinstance(field, GDT_Divider)]
        self.assertTrue(dividers)
        self.assertTrue(all(field.render_title() for field in dividers))

    def test_staff_can_change_another_users_setting(self):
        method = self.method_for_target()
        about_me = next(field for field in method.setting_fields() if field.get_name() == 'about_me')
        about_me.val('Edited by staff.')
        method.form_submitted()
        self.assertEqual('Edited by staff.', self.target.get_setting_val('about_me'))

    def test_datetime_settings_compare_at_millisecond_precision(self):
        field = GDT_DateTime('created')
        self.assertFalse(edit_user.setting_changed(
            field, '2026-08-27 12:34:56.123456', '2026-08-27 12:34:56.123'))
        self.assertTrue(edit_user.setting_changed(
            field, '2026-08-27 12:34:56.123456', '2026-08-27 12:34:56.124'))
        self.assertFalse(edit_user.setting_changed(
            field, '2026-08-27 12:34:00.000000', '2026-08-27T12:34'))

    def test_blank_password_does_not_replace_the_stored_password(self):
        field = GDT_Password('password').val(GDT_Password.hash('secret'))
        self.assertEqual('', field.html_value())
        self.assertFalse(edit_user.setting_changed(field, field.get_val(), None))

    def test_staff_gets_an_edit_link_in_the_profile_container(self):
        links = GDT_Container()
        module_admin().on_user_profile_links(self.target, links)
        fields = list(links.all_fields())
        self.assertEqual(1, len(fields))
        link = fields[0]
        self.assertIn(f'admin.edit_user.user.{self.target.get_id()}', link._href)


if __name__ == '__main__':
    unittest.main()
