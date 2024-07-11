from __future__ import annotations

import re
from datetime import timezone, datetime
from typing import Dict

from gdo.base.Application import Application
from gdo.base.Trans import tiso, t
from gdo.base.Util import Arrays
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
@version 8.0.0
"""


class Time:
    # Constants
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

    # @classmethod
    # def set_timezone_named(cls, timezone_name: str) -> None:
    #     """
    #     Set the timezone using a timezone name.
    #     """
    #     timezone_object = GDO_Timezone.get_by_name(timezone_name).getValue()
        # cls.set_timezone_gdo(timezone_object)

    # @classmethod
    # def set_timezone_gdo(cls, timezone_object):
    #     GDO_Timezone.table().get_by_id(timezone_object)
    #     pass

    @classmethod
    def get_timezone_object(cls, timezone_name: str):
        tz = GDO_Timezone.table().get_by_name(timezone_name)
        return timezone(tz.get_delta(), timezone_name)

    ############
    # Get Date #
    ############

    @classmethod
    def get_date(cls, time: float = None, fmt: str = '%Y-%m-%d %H:%M:%S.%f') -> str:
        """
        Get a formatted date string from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.
            fmt (str, optional): The format string. Defaults to '%Y-%m-%d %H:%M:%S.%f'.

        Returns:
            str: The formatted date string.
        """
        dt = cls.get_datetime(time)
        return dt.strftime(fmt) if dt else None

    @classmethod
    def get_datetime(cls, time: float = None) -> datetime:
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

    @classmethod
    def get_date_sec(cls, time: float = None) -> str:
        """
        Get a formatted date string without milliseconds from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.

        Returns:
            str: The formatted date string without milliseconds.
        """
        return cls.get_date(time, '%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_date_without_time(cls, time: float = None) -> str:
        """
        Get a date string without time part from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.

        Returns:
            str: The date string without time part.
        """
        return cls.get_date(time, '%Y-%m-%d')

    ###################
    # PARSE Timestamp #
    ###################

    @classmethod
    def parse_time(cls, date: str, tz: str = None, format: str = 'parse') -> float:
        return cls.parse_time_iso(Application.LANG_ISO, date, tz, format)

    @classmethod
    def parse_time_db(cls, date: str) -> float:
        return cls.parse_time(date, cls.UTC, 'db')

    @classmethod
    def parse_time_iso(cls, iso: str, date: str, tz: str = None, format: str = 'parse') -> float:
        datetime_obj = cls.parse_datetime_iso(iso, date, tz, format)
        return float(datetime_obj.timestamp()) if datetime_obj else None

    ##################
    # Parse Datetime #
    ##################

    @classmethod
    def parse_datetime(cls, date: str, tz: str = None, fmt: str = 'parse') -> None | datetime:
        return cls.parse_datetime_iso(Application.LANG_ISO, date, tz, fmt)

    @classmethod
    def parse_datetime_db(cls, date: str, tz: str = None) -> None | datetime:
        return cls.parse_datetime_iso('en', date, tz, 'db')

    @classmethod
    def parse_datetime_iso(cls, iso: str, date: str, tz: str = None, fmt: str = 'parse') -> None | datetime:
        if not date:
            return None

        date = date.replace('am', '').replace('pm', '').strip()

        if len(date) == 10:
            date += ' 00:00:00.000000'
        elif len(date) == 16:
            date += ':00.000000'
        elif len(date) == 19:
            date += '.000000'
        elif len(date) != 26:
            raise ValueError('Cannot parse invalid date format.')

        if fmt == 'db':
            fmt = '%Y-%m-%d %H:%M:%S.%f'
        else:
            fmt = tiso(iso, 'df_' + fmt)

        tz = tz or cls.TIMEZONE
        if tz == 'UTC':
            dt = datetime.strptime(date, fmt)
        else:
            tz = cls.get_timezone_object(tz)
            dt = datetime.strptime(date, fmt).replace(tzinfo=tz)
        return dt

    ###########
    # Display #
    ###########

    @classmethod
    def display_timestamp(cls, timestamp: float, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return cls.display_timestamp_iso(Application.LANG_ISO, timestamp, fmt, default, tz)

    @classmethod
    def display_timestamp_iso(cls, iso: str, timestamp: float, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        if timestamp <= 0:
            return default
        dt = datetime.utcfromtimestamp(timestamp)
        return cls.display_datetime_iso(iso, dt, fmt, default, tz)

    @classmethod
    def display_datetime_iso(cls, iso: str, datetime_obj: datetime = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        fmt = tiso(iso, "df_" + fmt)
        return cls.display_datetime_format(datetime_obj, fmt, default, tz)

    @classmethod
    def display_datetime_format(cls, datetime_obj: datetime = None, fmt: str = 'Y-m-d H:i:s.v', default: str = '---', tz: str = None) -> str:
        if not datetime_obj:
            return default
        tz = cls.get_timezone_object(tz or cls.TIMEZONE)
        dt = datetime.fromtimestamp(datetime_obj.timestamp()).replace(tzinfo=tz)
        return dt.strftime(fmt)

    @classmethod
    def display_date(cls, date: str = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return cls.display_date_iso(Application.LANG_ISO, date, fmt, default, tz)

    @classmethod
    def display_date_iso(cls, iso: str, date: str = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        if date is None:
            return default
        d = cls.parse_datetime_db(date)
        return cls.display_datetime_iso(iso, d, fmt, default, tz)

    @classmethod
    def display_datetime(cls, datetime_obj: datetime = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return cls.display_datetime_iso(Application.LANG_ISO, datetime_obj, fmt, default, tz)

    @classmethod
    def display_time_iso(cls, iso: str, time: datetime = None, fmt: str = 'short', default: str = '---', timezone_id: str = None) -> str:
        dt = cls.get_datetime(time)
        return cls.display_datetime_iso(iso, dt, fmt, default, timezone_id)

    ##############
    # Timestamps #
    ##############

    @classmethod
    def get_diff_date(cls, date_one: str, date_now: str) -> float:
        now = date_now or cls.get_date(Application.TIME)
        a = cls.parse_datetime_db(now)
        b = cls.parse_datetime_db(date_one)
        return (a - b).total_seconds()

    @classmethod
    def get_diff_time(cls, time_one: float, time_two: float = None) -> float:
        time_two = time_two if time_two is not None else Application.TIME
        a = cls.get_datetime(time_one)
        b = cls.get_datetime(time_two)
        return (a - b).total_seconds()

    @classmethod
    def get_time(cls, date: str = None) -> float:
        return cls.parse_time(date, cls.TIMEZONE, 'db') if date else Application.TIME

    #######
    # Age #
    #######
    @classmethod
    def get_time_ago(cls, date: str = None) -> float:
        return Application.TIME - cls.get_time(date)

    @classmethod
    def get_age_in_years(cls, duration: float) -> float:
        return duration / cls.ONE_YEAR

    @classmethod
    def display_age(cls, date: str = None) -> str:
        return cls.display_age_ts(cls.get_time(date))

    @classmethod
    def display_age_ts(cls, timestamp: float) -> str:
        return cls.human_duration(Application.TIME - timestamp)

    @classmethod
    def human_duration(cls, seconds: float, n_units: int = 2, with_millis: bool = True, remove_zero_units: bool = True) -> str:
        return cls.human_duration_iso(Application.LANG_ISO, seconds, n_units, with_millis, remove_zero_units)

    @classmethod
    def human_duration_iso(cls, iso: str, seconds: float, n_units: int = 2, with_millis: bool = True, remove_zero_units: bool = True) -> str:
        factors = cls._human_duration_factors(iso)
        return cls._human_duration_raw(seconds, n_units, factors, with_millis, remove_zero_units)

    @classmethod
    def _human_duration_factors(cls, iso: str):
        factors = {
            'tu_s': 60,
            'tu_m': 60,
            'tu_h': 24,
            'tu_d': 7,
            'tu_w': 52.14,
            'tu_y': 9999
        }
        back = {}
        for key, val in factors.items():
            back[tiso(iso, key)] = val
        return back

    @classmethod
    def _human_duration_raw(cls, seconds: float, n_units: int, units: dict, with_millis: bool = True, remove_zero_units: bool = True) -> str:
        seconds = abs(seconds)
        calculated = {}
        ms = int(seconds * 1000) % 1000 if with_millis else 0
        duration = int(seconds)
        for text, mod in units.items():
            duration *= 1000
            mod *= 1000
            remainder = (duration % mod) / 1000.0
            if int(remainder) > 0:
                calculated[text] = f"{int(remainder)}{text}"
            duration //= mod
            if duration == 0:
                break

        # if len(calculated) == 0:
        #     return f"0{next(iter(units))}"

        calculated = Arrays.reverse_dict(calculated)
        i = 0
        for key in list(calculated.keys()):
            i += 1
            if i > n_units:
                del calculated[key]
        calculated = list(calculated.values())
        if len(calculated) < n_units and with_millis:
            if ms > 0:
                calculated.append(f"%3dms" % ms)
        return ' '.join(calculated)

    @classmethod
    def display_age_iso(cls, date: str, iso: str) -> str:
        return cls.display_age_ts_iso(cls.get_time(date), iso)

    @classmethod
    def display_age_ts_iso(cls, timestamp: float, iso: str) -> str:
        return cls.human_duration_iso(iso, Application.TIME - timestamp)

    @classmethod
    def week_timestamp(cls, year: int, week: int) -> int:
        week_start = datetime.now(tz=cls.get_timezone_object(cls.UTC)).date().isoformat()
        week_start = datetime.fromisoformat(week_start).isocalendar()
        week_start = datetime.strptime(f'{year}-{week}-{week_start[2]}', '%G-%V-%u').timestamp()
        return int(week_start)

    @classmethod
    def human_duration_en(cls, seconds: float, n_units: int = 2, with_millis: bool = False) -> str:
        return cls.human_duration_iso('en', seconds, n_units)

    @classmethod
    def is_valid_duration(cls, duration: str, min_val: float = None, max_val: float = None) -> bool:
        seconds = cls.human_to_seconds(duration)
        if seconds is None or not isinstance(seconds, (int, float)):
            return False
        if min_val is not None and seconds < min_val:
            return False
        if max_val is not None and seconds > max_val:
            return False
        return True

    @classmethod
    def human_to_seconds(cls, duration: str) -> float | None:
        if duration is None:
            return None
        multi = {
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
        for match in re.finditer(r'(\d+)\s*([smhdwoy]{0,2})', duration):
            matches.append((int(match.group(1)), match.group(2)))
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

    @classmethod
    def is_sunday(cls, time: int = 0, timezone_id: str = 'UTC') -> bool:
        return cls.is_day(str(cls.SUNDAY), time, timezone_id)

    @classmethod
    def is_day(cls, day: str, time: int = 0, timezone_id: str = 'UTC') -> bool:
        time = time or datetime.now(tz=cls.get_timezone_object(timezone_id)).timestamp()
        dt = datetime.utcfromtimestamp(time).strftime('%u')
        return dt == day
