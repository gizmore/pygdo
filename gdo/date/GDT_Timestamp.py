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
        return f"{self._name} DATETIME({self._millis}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"

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
    def render_html(self):
        return Time.display_date(self.get_val(), self._date_format)

    def render_txt(self):
        return Time.display_date(self.get_val(), self._date_format)
