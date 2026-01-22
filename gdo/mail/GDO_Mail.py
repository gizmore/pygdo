from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_DateTime import GDT_DateTime


class GDO_Mail(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('mail_id'),
            GDT_User('mail_receiver').not_null(),
            GDT_Method('mail_method').not_null(),
            GDT_String('mail_args').maxlen(512).not_null(),
            GDT_Created('mail_created'),
            GDT_DateTime('mail_sent'),
        ]
