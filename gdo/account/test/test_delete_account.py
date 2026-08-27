import os
import unittest
from unittest.mock import patch

from gdo.account.method.delete_account import delete_account
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdotest.TestUtil import GDOTestCase, install_module


class DeleteAccountTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        install_module('account')
        loader.init_modules(True, True)
        Application.init_cli()
        loader.init_cli()

    async def create_user(self, name: str) -> GDO_User:
        user = await Web.get_server().get_or_create_user(name)
        user._authenticated = True
        Application.set_current_user(user)
        return user

    def method_for(self, user: GDO_User) -> delete_account:
        return (delete_account().env_user(user, True).env_server(Web.get_server()).
                env_session(GDO_Session.for_user(user)).env_mode(Mode.render_cli))

    async def test_01_disable_marks_account_deleted_and_notifies_staff(self):
        user = await self.create_user('delete_account_disable_test')
        method = self.method_for(user)
        with patch.object(method, 'send_staff_mail') as mail:
            await method.disable_user(user, 'No longer using this account.')
        self.assertTrue(user.is_deleted())
        mail.assert_called_once_with(user, 'disabled', 'No longer using this account.')

    async def test_02_prune_removes_account_and_notifies_staff(self):
        user = await self.create_user('delete_account_prune_test')
        user_id = user.get_id()
        method = self.method_for(user)
        with patch.object(method, 'send_staff_mail') as mail:
            await method.prune_user(user, '')
        self.assertIsNone(GDO_User.table().get_by_id(user_id))
        mail.assert_called_once_with(user, 'pruned', '')

    def test_03_reason_is_optional_and_both_actions_need_confirmation(self):
        form = delete_account().get_form()
        reason = form.get_field('reason')
        self.assertFalse(reason.is_not_null())
        self.assertIn('<textarea', reason.render_form())
        self.assertTrue(form.get_field('confirm').is_not_null())
        disable = form.actions().get_field('disable')
        prune = form.actions().get_field('prune')
        self.assertIn('window.confirm("Really disable this account?")', disable.attr('onclick'))
        self.assertIn('window.confirm("Really permanently prune this account?")', prune.attr('onclick'))


if __name__ == '__main__':
    unittest.main()
