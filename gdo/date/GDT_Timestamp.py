from gdo.core.GDT_String import GDT_String
from gdo.base.Trans import t


class GDT_Timestamp(GDT_String):

    _date_format: str

    def __init__(self, name):
        super().__init__(name)
        self._date_format = t('df_long')

    def render_html(self):
        return 'HO'
