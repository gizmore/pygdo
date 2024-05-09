from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Method import GDT_Method
from gdo.date.GDT_Created import GDT_Created


class GDO_Cronjob(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('cron_id'),
            GDT_Method('cron_method'),
            GDT_Created('cron_started'),
            GDT_Bool('cron_success').initial('2'),
        ]
