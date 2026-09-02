import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdotest.TestUtil import GDOTestCase, cli_gizmore, cli_plug, cli_user


class GrantTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        Application.init_cli()
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()
        self.owner = cli_gizmore()
        await GDO_UserPermission.grant(self.owner, 'owner')
        await GDO_UserPermission.grant(self.owner, 'staff')
        self.target = cli_user('grant_target')

    async def test_owner_can_grant_and_revoke_permission(self):
        listed = cli_plug(self.owner, f'$grant {self.target.get_name_sid()}')
        self.assertIn('has permissions: none', listed)

        granted = cli_plug(self.owner, f'$grant {self.target.get_name_sid()} staff')
        staff = GDO_Permission.get_by_name('staff')
        self.assertIn('Granted staff', granted)
        self.assertTrue(GDO_UserPermission.has_permission(self.target, staff))

        listed = cli_plug(self.owner, f'$grant {self.target.get_name_sid()}')
        self.assertIn('has permissions: staff', listed)

        revoked = cli_plug(self.owner, f'$grant --remove {self.target.get_name_sid()} staff')
        self.assertIn('Revoked staff', revoked)
        self.assertFalse(GDO_UserPermission.has_permission(self.target, staff))

    async def test_staff_can_only_manage_a_permission_they_have(self):
        staff = cli_user('grant_staff')
        await GDO_UserPermission.grant(staff, 'staff')
        output = cli_plug(staff, f'$grant {self.target.get_name_sid()} admin')
        self.assertIn('only grant or revoke permissions you have', output)

    async def test_grant_requires_staff_permission(self):
        member = cli_user('grant_member')

        output = cli_plug(member, f'$grant {self.target.get_name_sid()} staff')

        self.assertIn('need the staff permissions', output)
