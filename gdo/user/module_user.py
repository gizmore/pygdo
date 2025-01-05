from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.user.GDT_Gender import GDT_Gender


class module_user(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Gender('gender'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Timestamp('last_activity'),
        ]
