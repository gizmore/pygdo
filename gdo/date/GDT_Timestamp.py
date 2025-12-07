from gdo.core.GDT_String import GDT_String
from gdo.base.Trans import t
from gdo.date.Time import Time


class GDT_Timestamp(GDT_String):
    _date_format: str
    _millis: int

    def __init__(self, name):
        super().__init__(name)
        self._date_format = Time.FMT_LONG
        self._millis = 3

    def date_format(self, date_format: str):
        self._date_format = date_format
        return self

    def gdo_column_define(self) -> str:
        return f"{self._name} TIMESTAMP({self._millis}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"

    def get_date(self) -> str:
        return self.get_val()

    def get_timestamp(self) -> float:
        return Time.get_time(self.get_val())

    def to_value(self, val: str):
        if val is None:
            return None
        return Time.parse_datetime_db(val)

    ##########
    # Render #
    ##########
    def render_format(self, format: str = None) -> str:
        format = format or self._date_format
        if (val := self.get_val()) is None:
            return '---'
        if format == Time.FMT_AGO:
            return Time.human_duration(Time.get_time_ago(val))
        else:
            return Time.display_date(val, format)

    def render_html(self):
        date = self.get_val()
        disp = self.render_format()
        ts = Time.get_time(date)
        return f"<span class=\"gdt-timestamp\" data-ts=\"{ts}\">{disp}</span>"

    def render_txt(self):
        return self.render_format()

    def render_card(self) -> str:
        ago = '' if self._date_format == Time.FMT_AGO else self.render_format(Time.FMT_AGO)
        if ago: ago = f" ({ago})"
        return f'<p>{self.render_label()}: {self.render_format()}{ago}</p>'
