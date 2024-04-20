from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize, Mode
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_DateTime import GDT_DateTime


class GDO_Mail(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('mail_id'),
            GDT_String('mail_receiver'),
            GDT_String('mail_subject'),
            GDT_Serialize('mail_mail').mode(Mode.PICKLE),
            GDT_Created('mail_created'),
            GDT_DateTime('mail_sent'),
        ]
