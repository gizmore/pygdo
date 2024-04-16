from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.date.GDT_DateTime import GDT_DateTime
from gdo.mail.GDO_Mail import GDO_Mail
from gdo.mail.GDT_Email import GDT_Email


class module_mail(GDO_Module):

    def gdo_classes(self):
        return [
            GDO_Mail,
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Email('email'),
            GDT_DateTime('email_approved'),
        ]
