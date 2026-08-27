from math import floor

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_Text import GDT_Text
from gdo.core.GDT_Token import GDT_Token
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page
from gdo.user.GDT_Gender import GDT_Gender
from gdo.user.GDT_Level import GDT_Level
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class module_user(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('activity_accuracy').not_null().units(2, False).initial('5m'),
            GDT_Bool('show_userlist').not_null().initial('1'),
            GDT_Secret('user_link_pepper').not_null().initial(GDT_Token.random(32)),
        ]

    async def gdo_install(self):
        # A fresh installation needs one stable secret shared by web and Dog.
        from gdo.base.GDO_ModuleVal import GDO_ModuleVal
        if GDO_ModuleVal.table().get_by_id(self.get_id(), 'user_link_pepper') is None:
            await self.save_config_val('user_link_pepper', self.get_config_val('user_link_pepper'), force=True)

    def cfg_activity_accuracy(self) -> int:
        return self.get_config_value('activity_accuracy')

    def cfg_user_link_pepper(self) -> str:
        return self.get_config_val('user_link_pepper')

    def gdo_init(self):
        Application.EVENTS.subscribe('permission_granted', self.on_permission_granted)

    async def on_permission_granted(self, user: GDO_User, perm_name: str):
        Cache.remove('users_with_permission')

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Gender('gender'),
            GDT_Text('about_me'),
            GDT_Link('connect_account').href(self.href('connect')).text('link_connect_account'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Timestamp('last_activity'),
            GDT_Level('level').initial('0'),
        ]

    def get_activity_cut_date(self) -> str:
        if seconds := int(self.cfg_activity_accuracy()):
            return Time.get_date(int(floor(Application.TIME / seconds) * seconds))
        return Time.get_date(Application.TIME)

    def set_last_activity(self, user: GDO_User):
        # TCP uses Ghost until tcpauth completes. A Ghost may carry the
        # synthetic id 0, but it must never create a user-setting row.
        if self.cfg_activity_accuracy() and not user.is_ghost() and user.is_persisted():
            user.save_setting('last_activity', self.get_activity_cut_date())

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_user():
            page._right_bar.add_field(GDT_ProfileLink().user(user))
        if self.get_config_value('show_userlist'):
            page._left_bar.add_field(GDT_Link().href(self.href('ranking')).text('mt_user_ranking'))
