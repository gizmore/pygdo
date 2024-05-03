from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Char import GDT_Char


class GDO_Language(GDO):

    def gdo_columns(self):
        return [
            GDT_AutoInc('lang_id'),
            GDT_Char('lang_iso').not_null().ascii().maxlen(2),
        ]
