from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.date.Time import Time
from gdo.mail.GDO_Mail import GDO_Mail
from gdo.mail.GDT_Email import GDT_Email
from gdo.ui.GDT_Link import GDT_Link


class module_mail(GDO_Module):

    def gdo_classes(self):
        return [
            GDO_Mail,
        ]

    def gdo_friendencies(self) -> list:
        return [
            'gpg',
        ]

    def gdo_user_config(self) -> list[GDT]:
        from gdo.date.GDT_DateTime import GDT_DateTime
        return [
            GDT_Email('email').obfuscate(),
            GDT_DateTime('email_confirmed'),
            GDT_Link('change_mail').href(self.href('change_mail')).text('link_change_mail'),
        ]

    def set_email_for(self, user: GDO_User, email: str, confirmed: bool = True):
        user.save_setting('email', email)
        if confirmed:
            self.set_mail_confirmed_for(user)

    def set_mail_confirmed_for(self, user: GDO_User):
        user.save_setting('email_confirmed', Time.get_date())
