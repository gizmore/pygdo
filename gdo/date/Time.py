from __future__ import annotations

from datetime import timezone, datetime
from typing import Dict

import pytz

from gdo.base.Application import Application
from gdo.base.Trans import tiso
from gdo.date.GDO_Timezone import GDO_Timezone


"""
Time utility.
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

    ################
    ### TIMEZONE ###
    ################

    @classmethod
    def set_timezone_named(cls, timezone_name: str) -> None:
        """
        Set the timezone using a timezone name.
        """
        # timezone_object = GDO_Timezone.get_by_name(timezone_name).getValue()
        # cls.set_timezone_gdo(timezone_object)

    @classmethod
    # def set_timezone_gdo(cls, timezone_object):
    #     GDO_Timezone.table().get_by_id(timezone_object)
    #     pass

    @classmethod
    def get_timezone_object(cls, timezone_name: str):
        tz = GDO_Timezone.table().get_by_name(timezone_name)
        return timezone(tz.get_delta(), timezone_name)

    ############
    # GET DATE #
    ############

    @classmethod
    def get_date(cls, time: float = None, _format: str = '%Y-%m-%d %H:%M:%S.%f') -> str:
        """
        Get a formatted date string from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.
            _format (str, optional): The format string. Defaults to '%Y-%m-%d %H:%M:%S.%f'.

        Returns:
            str: The formatted date string.
        """
        dt = cls.get_datetime(time)
        return dt.strftime(_format) if dt else None

    @classmethod
    def get_datetime(cls, time: float = None) -> datetime:
        """
        Get a datetime object from a timestamp.

        Args:
            time (float, optional): The timestamp. Defaults to 0.

        Returns:
            datetime: The datetime object.
        """
        if time is None:
            time = Application.TIME

        return datetime.utcfromtimestamp(time).replace(tzinfo=timezone.utc)

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

    # PARSE Timestamp

    @classmethod
    def parse_date_db(cls, date: str) -> float:
        return cls.parse_date(date, cls.UTC, 'db')

    @classmethod
    def parse_date(cls, date: str, tz: str = None, _format: str = 'parse') -> float:
        return cls.parse_date_iso(Application.LANG_ISO, date, tz, _format)

    @classmethod
    def parse_date_iso(cls, iso: str, date: str, tz: str = None, format: str = 'parse') -> float:
        datetime_obj = cls.parse_datetime_iso(iso, date, tz, format)
        return float(datetime_obj.timestamp()) if datetime_obj else None

    # Parse Datetime

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

    # Display

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
        if not d:
            return default
        return cls.display_datetime_iso(iso, d, fmt, default, tz)

    @classmethod
    def display_datetime(cls, datetime_obj: datetime = None, fmt: str = 'short', default: str = '---', tz: str = None) -> str:
        return cls.display_datetime_iso(Application.LANG_ISO, datetime_obj, fmt, default, tz)

    @classmethod
    def display_time_iso(cls, iso: str, time: datetime = None, fmt: str = 'short', default: str = '---', timezone_id: str = None) -> str:
        dt = cls.get_datetime(time)
        return cls.display_datetime_iso(iso, dt, fmt, default, timezone_id)

