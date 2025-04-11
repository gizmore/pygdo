from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.date.GDO_Timezone import GDO_Timezone


class module_date(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 5

    def gdo_classes(self) -> list:
        return [
            GDO_Timezone,
        ]

    def gdo_install(self):
        from gdo.date.DateInstall import DateInstall
        DateInstall.now(self)

    def gdo_user_settings(self) -> list[GDT]:
        from gdo.date.GDT_Timezone import GDT_Timezone
        return [
            GDT_Timezone('timezone').not_null().initial('1'),
        ]
