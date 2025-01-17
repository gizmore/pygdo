from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdo.user.GDT_Gender import GDT_Gender


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

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Gender('gender'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Timestamp('last_activity'),
        ]

    def set_last_activity(self, user: GDO_User):
        if seconds := int(self.cfg_activity_accuracy()):
            user.save_setting('last_activity', Time.get_date(int(round(Application.TIME / seconds) * seconds)))
