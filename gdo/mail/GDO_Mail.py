from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_DateTime import GDT_DateTime


class GDO_Mail(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('mail_id'),
            GDT_String('mail_receiver'),
            GDT_String('mail_subject'),
            GDT_Text('mail_mail').maxlen(2**20),
            GDT_Created('mail_created'),
            GDT_DateTime('mail_sent'),
        ]
