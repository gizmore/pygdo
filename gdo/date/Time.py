import re
from datetime import timezone, datetime
from functools import lru_cache
from typing import Dict

from gdo.base.Application import Application
from gdo.base.Trans import tiso
from gdo.date.GDO_Timezone import GDO_Timezone

"""
Time utility.
In the language file are various date format templates.
Important are df_db and df_parse.
Method namings follow these conventions in signature elements:
 - time | a timestamp as float
 - date | a string in database format. Uses df_db
 - datetime | a python datetime object
 - tz | a timezone string like Europe/Berlin or UTC
 - tzid | a [GDO_Timezone](../g) object
@version 8.0.2
"""


class Time:
    # Constants
    ONE_MICROSECOND = 0.000001 # yes. this is even used and shown in page timings sometimes =) 03.May.2025 by gizmore!!!
    ONE_MILLISECOND = 0.001
    ONE_SECOND = 1
    ONE_MINUTE = 60
    ONE_HOUR = 3600
    ONE_DAY = 86400
    ONE_WEEK = 604800
    ONE_MONTH = 2629800
    ONE_YEAR = 31557600

    # Display formats
    FMT_MINUTE = 'minute'
    FMT_SHORT = 'short'
    FMT_LONG = 'long'
    FMT_DAY = 'day'  # Date format FMT_DAY is same as FMT_SHORT.
    FMT_MS = 'ms'
    FMT_DB = 'db'
    FMT_AGO = 'ago'
    FMT_TIME_ONLY = 'clock'

    # Timezone constants
    UTC = '1'
    TIMEZONE = 'UTC'

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    # Timezone conversion
    TIMEZONE_OBJECTS: Dict[str, timezone] = {}

    #############
    # Timezones #
    #############

    @staticmethod
    def get_timezone_object(timezone_name: str):
        tz = GDO_Timezone.table().get_by_name(timezone_name)
        return timezone(tz.get_delta(), timezone_name)

    ############
    # Get Date #
    ############

    @staticmethod
    def get_date(time: float = None, fmt: str = '%Y-%m-%d %H:%M:%S.%f') -> str:
        """
        Get a formatted date string from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.
            fmt (str, optional): The format string. Defaults to '%Y-%m-%d %H:%M:%S.%f'.

        Returns:
            str: The formatted date string.
        """
        dt = Time.get_datetime(time)
        return dt.strftime(fmt) if dt else None

    @staticmethod
    def get_datetime(time: float = None) -> datetime:
        """
        Get a datetime object from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to Application.TIME.

        Returns:
            datetime: The datetime object.
        """
        if time is None:
            time = Application.TIME

        return datetime.fromtimestamp(time, tz=timezone.utc)

    @staticmethod
    def get_date_sec(time: float = None) -> str:
        """
        Get a formatted date string without milliseconds from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.

        Returns:
            str: The formatted date string without milliseconds.
        """
        return Time.get_date(time, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_date_without_time(time: float = None) -> str:
        """
        Get a date string without time part from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.

        Returns:
            str: The date string without time part.
        """
        return Time.get_date(time, '%Y-%m-%d')

    ###################
    # PARSE Timestamp #
    ###################

    @staticmethod
    def parse_time(date: str, tz: str = None, format: str = 'parse') -> float:
        return Time.parse_time_iso(Application.LANG_ISO, date, tz, format)

    @staticmethod
    def parse_time_db(date: str) -> float:
        return Time.parse_time(date, Time.TIMEZONE, 'db')

    @staticmethod
    def parse_time_iso(iso: str, date: str, tz: str = None, format: str = 'parse') -> float:
        datetime_obj = Time.parse_datetime_iso(iso, date, tz, format)
        return float(datetime_obj.timestamp()) if datetime_obj else None

    ##################
    # Parse Datetime #
    ##################

    @staticmethod
    def parse_datetime(date: str, tz: str = None, fmt: str = 'parse') -> None | datetime:
        return Time.parse_datetime_iso(Application.LANG_ISO, date, tz, fmt)

    @staticmethod
    def parse_datetime_db(date: str, tz: str = TIMEZONE) -> None | datetime:
        return Time.parse_datetime_iso('en', date, tz, 'db')

    @staticmethod
    def parse_datetime_iso(iso: str, date: str, tz: str = None, fmt: str = 'parse') -> None | datetime:
        if not date:
            return None

        date = date.replace('am', '').replace('pm', '').strip()

        if len(date) == 10:
            date += ' 00:00:00.000000'
        elif len(date) == 16:
            date += ':00.000000'
        elif len(date) == 19:
            date += '.000000'
        elif len(date) == 23:
            date += '000'
        elif len(date) != 26:
            raise ValueError(f"Cannot parse invalid date format: {date}")

        if fmt == 'db':
            fmt = '%Y-%m-%d %H:%M:%S.%f'
        else:
            fmt = tiso(iso, 'df_' + fmt)

        tz = tz or Time.TIMEZONE
        if tz == 'UTC':
            dt = datetime.strptime(date, fmt)
        else:
            tz = Time.get_timezone_object(tz)
            dt = datetime.strptime(date, fmt).replace(tzinfo=tz)
        return dt

    ###########
    # Display #
    ###########

    @staticmethod
    def display_timestamp(timestamp: float, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return Time.display_timestamp_iso(Application.LANG_ISO, timestamp, fmt, default, tz)

    @staticmethod
    def display_timestamp_iso(iso: str, timestamp: float, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        if timestamp <= 0:
            return default
        dt = datetime.fromtimestamp(timestamp, Time.get_timezone_object(tz or Time.TIMEZONE))
        return Time.display_datetime_iso(iso, dt, fmt, default, tz)

    @staticmethod
    def display_datetime_iso(iso: str, datetime_obj: datetime = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        fmt = tiso(iso, "df_" + fmt)
        return Time.display_datetime_format(datetime_obj, fmt, default, tz)

    @staticmethod
    def display_datetime_format(datetime_obj: datetime = None, fmt: str = 'Y-m-d H:i:s.v', default: str = '---', tz: str = None) -> str:
        if not datetime_obj:
            return default
        tz = Time.get_timezone_object(tz or Time.TIMEZONE)
        dt = datetime.fromtimestamp(datetime_obj.timestamp()).replace(tzinfo=tz)
        return dt.strftime(fmt)

    @staticmethod
    def display_date(date: str = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return Time.display_date_iso(Application.LANG_ISO, date, fmt, default, tz)

    @staticmethod
    def display_date_iso(iso: str, date: str = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        if date is None:
            return default
        d = Time.parse_datetime_db(date)
        return Time.display_datetime_iso(iso, d, fmt, default, tz)

    @staticmethod
    def display_datetime(datetime_obj: datetime = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return Time.display_datetime_iso(Application.LANG_ISO, datetime_obj, fmt, default, tz)

    @staticmethod
    def display_time_iso(iso: str, time: datetime = None, fmt: str = 'short', default: str = '---', timezone_id: str = None) -> str:
        dt = Time.get_datetime(time)
        return Time.display_datetime_iso(iso, dt, fmt, default, timezone_id)

    ##############
    # Timestamps #
    ##############

    @staticmethod
    def get_diff_date(date_one: str, date_now: str) -> float:
        now = date_now or Time.get_date(Application.TIME)
        a = Time.parse_datetime_db(now)
        b = Time.parse_datetime_db(date_one)
        return (a - b).total_seconds()

    @staticmethod
    def get_diff_time(time_one: float, time_two: float = None) -> float:
        time_two = time_two if time_two is not None else Application.TIME
        a = Time.get_datetime(time_one)
        b = Time.get_datetime(time_two)
        return (a - b).total_seconds()

    @staticmethod
    def get_time(date: str = None) -> float:
        return Time.parse_time(date, 'UTC', 'db') if date else Application.TIME

    #######
    # Age #
    #######
    @staticmethod
    def get_time_ago(date: str = None) -> float:
        return Application.TIME - Time.get_time(date)

    @staticmethod
    def get_age_in_years(duration: float) -> float:
        return duration / Time.ONE_YEAR

    @staticmethod
    def display_age(date: str = None) -> str:
        return Time.display_age_ts(Time.get_time(date))

    @staticmethod
    def display_age_ts(timestamp: float) -> str:
        return Time.human_duration(Application.TIME - timestamp)

    @staticmethod
    def human_duration(seconds: float, n_units: int = 2, with_millis: bool = True, remove_zero_units: bool = True) -> str:
        return Time.human_duration_iso(Application.LANG_ISO, seconds, n_units, with_millis)

    @staticmethod
    def human_duration_iso(iso: str, seconds: float, n_units: int = 2, with_millis: bool = True) -> str:
        factors = Time._human_duration_factors(iso)
        return Time._human_duration_raw(seconds, n_units, factors, with_millis)

    @staticmethod
    @lru_cache(maxsize=None)
    def _human_duration_factors(iso: str):
        factors = {
            'tu_us': 1000000,
            'tu_ms': 1000,
            'tu_s': 60,
            'tu_m': 60,
            'tu_h': 24,
            'tu_d': 7,
            'tu_w': 52.14,
            'tu_y': 9999,
        }
        return {tiso(iso, key): val for key, val in factors.items()}

    @staticmethod
    def _human_duration_raw(seconds: float, n_units: int, factors: dict, with_millis: bool = True) -> str:
        values = []
        factor_keys = list(factors.keys())
        if with_millis:
            for unit in factor_keys[:2]:  # 'us' and 'ms'
                remainder = seconds * factors[unit]
                remainder, value = divmod(remainder, 1000)
                if value >= 1: values.append((value, unit))
        remainder = round(seconds)
        for unit in factor_keys[2:]:  # 's' and above
            remainder, value = divmod(remainder, factors[unit])
            if value: values.append((value, unit))
        result = " ".join(["%d%s" % (v, u) for v, u in reversed(values[-n_units:]) if v])
        return result if result else "0s"

    @staticmethod
    def display_age_iso(date: str, iso: str) -> str:
        return Time.display_age_ts_iso(Time.get_time(date), iso)

    @staticmethod
    def display_age_ts_iso(timestamp: float, iso: str) -> str:
        return Time.human_duration_iso(iso, Application.TIME - timestamp)

    @staticmethod
    def week_timestamp(year: int, week: int) -> int:
        week_start = datetime.now(tz=Time.get_timezone_object(Time.UTC)).date().isoformat()
        week_start = datetime.fromisoformat(week_start).isocalendar()
        week_start = datetime.strptime(f'{year}-{week}-{week_start[2]}', '%G-%V-%u').timestamp()
        return int(week_start)

    @staticmethod
    def human_duration_en(seconds: float, n_units: int = 2, with_millis: bool = False) -> str:
        return Time.human_duration_iso('en', seconds, n_units, with_millis)

    @staticmethod
    def is_valid_duration(duration: str, min_val: float = None, max_val: float = None) -> bool:
        seconds = Time.human_to_seconds(duration)
        if seconds is None or not isinstance(seconds, (int, float)):
            return False
        if min_val is not None and seconds < min_val:
            return False
        if max_val is not None and seconds > max_val:
            return False
        return True

    @staticmethod
    def human_to_seconds(duration: str) -> float | None:
        if duration is None:
            return None
        multi = {
            'ns': 0.000000001,
            'µs': 0.000001,
            'ms': 0.001,
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
            'mo': 2592000,
            'y': 31536000,
        }
        matches = []
        for match in re.finditer(r'([.\d]+)\s*([suµnmhdwoy]{0,2})', duration):
            matches.append((float(match.group(1)), match.group(2)))
        back = 0.0
        for match in matches:
            d, unit = match
            unit_mult = multi.get(unit, 1.0)
            back += d * unit_mult
        return float(back)

    @staticmethod
    def get_year(date: str) -> str:
        return date[:4]

    @staticmethod
    def get_month(date: str) -> str:
        return date[5:7]

    @staticmethod
    def get_day(date: str) -> str:
        return date[8:10]

    @staticmethod
    def is_sunday(time: int = 0, timezone_id: str = 'UTC') -> bool:
        return Time.is_day(str(Time.SUNDAY), time, timezone_id)

    @staticmethod
    def is_day(day: str, time: int = 0, timezone_id: str = 'UTC') -> bool:
        time = time or datetime.now(tz=Time.get_timezone_object(timezone_id)).timestamp()
        dt = datetime.fromtimestamp(time).strftime('%u')
        return dt == day
