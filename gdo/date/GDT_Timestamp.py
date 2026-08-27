import re
from datetime import datetime

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import tpl
from gdo.date.Time import Time


class GDT_Timestamp(GDT_String):
    _date_format: str
    _millis: int

    def __init__(self, name):
        super().__init__(name)
        self.icon('calendar')
        self._date_format = Time.FMT_AGO
        self._millis = 3
        self._input_type = 'datetime-local'
        self.attr('step', self.html_step())

    def html_step(self) -> str:
        return '1' if self._millis == 0 else f"0.{('0' * (self._millis - 1))}1"

    def milliseconds(self, val: str | None) -> str:
        """Normalize a datetime-local value to this field's DB precision."""
        val = (val or '').replace('T', ' ', 1)
        if not val:
            return ''
        # A nullable timestamp can arrive from an empty database setting as a
        # bare fractional part (for example ``.000``).  Do not turn that into
        # an invalid pseudo-date such as ``.000.000``: it must remain empty.
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2}(?:\.\d{0,6})?)?', val):
            return ''
        if len(val) == 16:  # YYYY-MM-DD HH:MM
            val += ':00'
        if self._millis == 0:
            return val[:19]
        fraction = val[20:] if len(val) > 19 and val[19] == '.' else ''
        return f"{val[:19]}.{fraction[:self._millis].ljust(self._millis, '0')}"

    def val(self, val: str | list):
        # datetime-local posts ISO-local values while database timestamps use
        # a space separator.
        if isinstance(val, str):
            val = self.milliseconds(val)
        return super().val(val)

    def html_value(self):
        val = self.get_val()
        if val is None:
            return ''
        # HTML datetime-local accepts the database timestamp's precision.
        return Strings.html(self.milliseconds(val).replace(' ', 'T', 1))

    def date_format(self, date_format: str):
        self._date_format = date_format
        return self

    def gdo_column_define(self) -> str:
        return f"{self._name} TIMESTAMP({self._millis}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"

    def filter_has_date(self) -> bool:
        return True

    def filter_has_time(self) -> bool:
        return True

    def render_table_filter(self, vals: dict) -> str:
        return tpl('date', 'filter_datetime.html', vals)

    @staticmethod
    def filter_date(value: str) -> str | None:
        if not value or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            return None
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return None
        return value

    @staticmethod
    def filter_time(value: str, end: bool = False) -> str | None:
        if not value or not re.fullmatch(r'\d{2}:\d{2}(?::\d{2})?', value):
            return None
        try:
            datetime.strptime(value, '%H:%M' if len(value) == 5 else '%H:%M:%S')
        except ValueError:
            return None
        if len(value) == 5:
            return value + (':59.999' if end else ':00')
        return value + ('.999' if end else '')

    def gdo_filter_query(self, gdo: 'GDO', query: 'Query'):
        values = self.get_val()
        if not isinstance(values, dict):
            return super().gdo_filter_query(gdo, query)

        date_from = self.filter_date(values.get('date_from', '')) if self.filter_has_date() else None
        date_to = self.filter_date(values.get('date_to', '')) if self.filter_has_date() else None
        time_from = self.filter_time(values.get('time_from', '')) if self.filter_has_time() else None
        time_to = self.filter_time(values.get('time_to', ''), True) if self.filter_has_time() else None
        field = self.get_name()

        if not self.filter_has_time():
            if date_from and date_to:
                query.where(f"{field} BETWEEN {GDT.quote(date_from)} AND {GDT.quote(date_to)}")
            elif date := date_from or date_to:
                query.where(f"{field}={GDT.quote(date)}")
            return

        # One selected date means that calendar day, not an unbounded range
        # starting or ending at midnight.  Any entered time narrows the
        # corresponding side of that day.
        if date_from and not date_to:
            date_to = date_from
        elif date_to and not date_from:
            date_from = date_to

        if date_from:
            start = date_from if not self.filter_has_time() else f"{date_from} {time_from or '00:00:00'}"
            query.where(f"{field}>={GDT.quote(start)}")
        elif time_from:
            condition = f"{field}>={GDT.quote(time_from)}" if not self.filter_has_date() else f"TIME({field})>={GDT.quote(time_from)}"
            query.where(condition)

        if date_to:
            end = date_to if not self.filter_has_time() else f"{date_to} {time_to or '23:59:59.999'}"
            query.where(f"{field}<={GDT.quote(end)}")
        elif time_to:
            condition = f"{field}<={GDT.quote(time_to)}" if not self.filter_has_date() else f"TIME({field})<={GDT.quote(time_to)}"
            query.where(condition)

    def get_date(self) -> str:
        return self.get_val()

    def get_timestamp(self) -> float:
        return Time.get_time(self.get_val())

    def get_elapsed(self) -> float:
        return Application.TIME - self.get_timestamp()

    def to_value(self, val: str):
        return Time.parse_datetime_db(val) if val else None

    ##########
    # Render #
    ##########
    def render_format(self, format: str = None) -> str:
        format = format or self._date_format
        if (val := self.get_val()) is None:
            return '---'
        if format == Time.FMT_BOTH_FULL:
            return f'{self.render_format(Time.FMT_LONG)} ({self.render_format(Time.FMT_AGO)})'
        if format == Time.FMT_AGO:
            self.attr('title', Time.display_date(val))
            self.attr('gdo-ts', str(Time.get_time(val)))
            return Time.human_duration(Time.get_time_ago(val))
        else:
            return Time.display_date(val, format)

    def render_html(self):
        date = self.get_val()
        disp = self.render_format()
        ts = Time.get_time(date)
        return f"<span class=\"gdt-timestamp {self._date_format}\"{self.html_attrs()} data-ts=\"{ts}\">{disp}</span>"

    def render_txt(self):
        return self.render_format()

    def render_card(self) -> str:
        return f'<p>{self.render_card_label()}: {self.render_format(Time.FMT_BOTH_FULL)}</p>'
