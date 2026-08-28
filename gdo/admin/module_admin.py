from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_admin(GDO_Module):

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe('user_profile_links', self.on_user_profile_links)

    def on_user_profile_links(self, user: GDO_User, links):
        if GDO_User.current().is_staff():
            links.add_field(GDT_Link().href(self.href('edit_user', f'&user={user.get_id()}')).icon('edit').text('link_edit'))

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_admin():
            page._right_bar.add_field(GDT_Link().href(self.href('modules')).text('module_admin').icon('settings'))

    def gdo_admin_links(self) -> list['GDT_Link']:
        return [
            GDT_Link().href(self.href('users')).text('mt_admin_users'),
            GDT_Link().href(self.href('login_as')).text('mt_admin_login_as'),
        ]
