from math import floor

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdo.user.GDT_Gender import GDT_Gender
from gdo.user.GDT_Level import GDT_Level


class module_user(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('activity_accuracy').not_null().units(2, False).initial('5m'),
        ]

    def cfg_activity_accuracy(self) -> int:
        return self.get_config_value('activity_accuracy')

    def gdo_init(self):
        Application.EVENTS.subscribe('permission_granted', self.on_permission_granted)

    async def on_permission_granted(self, user: GDO_User, perm_name: str):
        Cache.remove('users_with_permission')

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Gender('gender'),
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
        if self.cfg_activity_accuracy() and user.is_persisted():
            user.save_setting('last_activity', self.get_activity_cut_date())
