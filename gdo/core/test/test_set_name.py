import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdotest.TestUtil import GDOTestCase, cli_gizmore, cli_plug, cli_user


class SetNameTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        Application.init_cli()
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()
        self.staff = cli_gizmore()
        await GDO_UserPermission.grant(self.staff, 'staff')
        self.target = cli_user('set_name_target')

    async def test_staff_can_set_a_user_displayname(self):
        output = cli_plug(self.staff, f'$name {self.target.get_name_sid()} RenamedTarget')

        self.assertIn('displayname has been set to RenamedTarget', output)
        self.assertEqual('RenamedTarget', self.target.gdo_val('user_displayname'))

    async def test_member_cannot_set_a_user_displayname(self):
        member = cli_user('set_name_member')
        output = cli_plug(member, f'$name {self.target.get_name_sid()} ForbiddenName')

        self.assertIn('need the staff permissions', output)
