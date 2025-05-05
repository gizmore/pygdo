from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time
from gdo.date.GDT_Created import GDT_Created


class GDO_Cronjob(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('cron_id'),
            GDT_Method('cron_method').not_null(),
            GDT_Bool('cron_success').not_null().initial('2'),
            GDT_String('cron_error').maxlen(1024),
            GDT_Created('cron_started'),
        ]

    @classmethod
    def cleanup(cls):
        cut = Time.get_date(Application.TIME - Time.ONE_MONTH * 1.0337)
        return cls.table().delete_where(f"cron_started < '{cut}'")
