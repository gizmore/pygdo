from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_account(GDO_Module):

    def gdo_dependencies(self) -> list:
        return [
        ]

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_user():
            page._right_bar.add_field(GDT_Link().href(self.href('all_settings')).text('link_settings').icon('account'))


    def gdo_user_config(self) -> list[GDT]:
        return [
            # This is an account-management action, not public profile data.
            # all_settings() renders links explicitly, whereas the profile skips hidden fields.
            GDT_Link('delete_account').href(self.href('delete_account')).text('delete_account').hidden(),
        ]
