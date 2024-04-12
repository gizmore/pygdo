from datetime import datetime

import pytz

from gdo.date import module_date
from gdo.date.GDO_Timezone import GDO_Timezone
from gdo.date.Time import Time


class DateInstall:

    BULK = []

    @classmethod
    def now(cls, module: module_date):
        cls.install_timezone('UTC', 0)
        cls.install_timezone('USRT', 0)
        cls.install_timezone('FAMT', 0)
        for tz in pytz.all_timezones:
            cls.install_timezone(tz)
        GDO_Timezone.table().bulk_insert_gdo(cls.BULK)

    @classmethod
    def install_timezone(cls, tz_name, offset=None):
        if offset is None:
            offset = cls.get_timezone_offset(tz_name)
        if not GDO_Timezone.get_by_name(tz_name):
            gdo_tz = GDO_Timezone.blank({
                'tz_id': '0',
                'tz_name': tz_name,
                'tz_offset': str(offset)
            })
            cls.BULK.append(gdo_tz)

    @classmethod
    def get_timezone_offset(cls, timezone_name) -> int:
        tz = pytz.timezone(timezone_name)
        return int(tz.utcoffset(datetime.utcnow()).total_seconds())
