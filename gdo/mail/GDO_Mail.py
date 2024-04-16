from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Serialize import GDT_Serialize


class GDO_Mail(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('mail_id'),
            GDT_Serialize('mail_mail'),
        ]
