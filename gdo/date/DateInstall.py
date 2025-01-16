from datetime import datetime
from zoneinfo import ZoneInfo

import pytzdata

from gdo.date import module_date
from gdo.date.GDO_Timezone import GDO_Timezone


class DateInstall:
    BULK = []
    HAVE = []

    @classmethod
    def now(cls, module: module_date):
        cls.load_timezones()
        cls.install_timezone('UTC', 0)
        cls.install_timezone('USRT', 0)
        cls.install_timezone('FAMT', 31337)
        for tz in pytzdata.get_timezones():
            if tz != 'UTC':
                cls.install_timezone(tz)
        GDO_Timezone.table().bulk_insert_gdo(cls.BULK)

    @classmethod
    def load_timezones(cls):
        cls.HAVE = GDO_Timezone.table().select('tz_name').exec().fetch_column()

    @classmethod
    def install_timezone(cls, tz_name: str, offset=None):
        if offset is None:
            offset = cls.get_timezone_offset(tz_name)
        if tz_name not in cls.HAVE:
            gdo_tz = GDO_Timezone.blank({
                'tz_id': '0',
                'tz_name': tz_name,
                'tz_offset': str(offset)
            })
            if tz_name == 'UTC':
                gdo_tz.insert()
            else:
                cls.BULK.append(gdo_tz)

    @classmethod
    def get_timezone_offset(cls, timezone_name) -> int:
        dt = datetime.now(tz = ZoneInfo(timezone_name))
        return int(dt.utcoffset().total_seconds())
