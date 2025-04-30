from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Char import GDT_Char
from gdo.core.GDT_String import GDT_String


class GDO_Language(GDO):

    def gdo_columns(self):
        return [
            GDT_AutoInc('lang_id'),
            GDT_Char('lang_iso').not_null().ascii().maxlen(2),
            GDT_String('lang_english').maxlen(48).ascii().not_null(),
            GDT_String('lang_native').maxlen(48).not_null(),
            GDT_Bool('lang_supported').not_null().initial('0'),
        ]
