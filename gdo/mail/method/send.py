from gdo.base.Method import Method
from gdo.base.GDT import GDT
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User
from gdo.mail.Mail import Mail
from gdo.ui.GDT_Title import GDT_Title


class send(Method):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User("to").not_null(),
            GDT_Title("subject").not_null(),
            GDT_RestOfText("body").not_null()
        ]

    def gdo_execute(self) -> GDT:
        sender = self._env_user
        to = self.param_value('to')
        if not to.has_mail():
            return self.error('err_user_no_mail')
        mail = Mail.from_bot()
        mail.reply_to(sender.get_mail())
        mail.subject(self.param_val('subject'))
        mail.body(self.param_value('body'))
        mail.send_to_user(to)
