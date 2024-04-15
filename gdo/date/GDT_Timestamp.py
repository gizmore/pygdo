from gdo.core.GDT_String import GDT_String
from gdo.base.Trans import t


class GDT_Timestamp(GDT_String):
    _date_format: str
    _millis: int

    def __init__(self, name):
        super().__init__(name)
        self._date_format = t('df_long')
        self._millis = 6

    def gdo_column_define(self) -> str:
        return f"{self._name} DATETIME({self._millis}){self.gdo_column_define_null()}{self.gdo_column_define_default()}"

    def render_html(self):
        return 'HO'
