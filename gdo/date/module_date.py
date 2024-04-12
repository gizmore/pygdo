from gdo.base.GDO_Module import GDO_Module
from gdo.date.DateInstall import DateInstall
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
        DateInstall.now(self)
