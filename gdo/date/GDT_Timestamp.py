from gdo.core.GDT_String import GDT_String
from gdo.base.Trans import t
from gdo.date.Time import Time


class GDT_Timestamp(GDT_String):
    _date_format: str
    _millis: int

    def __init__(self, name):
        super().__init__(name)
        self._date_format = 'long'
        self._millis = 6

    def gdo_column_define(self) -> str:
        return f"{self._name} DATETIME({self._millis}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"

    def get_date(self) -> str:
        return self.get_val()

    def get_timestamp(self) -> float:
        return Time.get_time(self.get_val())

    ##########
    # Render #
    ##########
    def render_html(self):
        return Time.display_date(self.get_val(), self._date_format)
