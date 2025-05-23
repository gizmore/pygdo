from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t, sitename
from gdo.base.Util import Strings
from gdo.core import module_core
from gdo.mail.Mail import Mail
from gdo.net.GDT_Url import GDT_Url
from gdo.ui.GDT_Error import GDT_Error


class not_found(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Url("_url").internal().not_null(),
        ]

    def gdo_execute(self) -> GDT:
        if module_core.instance().cfg_404_mails():
            self.send_mail()
        url = self.param_val('_url')
        Application.status("404 Not Found")
        return GDT_Error().title('module_core').text('err_not_found', (Strings.html(f'"{url}"'),))

    def send_mail(self):
        mail = Mail.from_bot()
        mail.subject(t('mails_error', (sitename(), 404)))
        mail.body(t('mailb_error'))
        mail.send()
