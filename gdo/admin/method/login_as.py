from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Trans import Trans
from gdo.base.Util import module_enabled
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class login_as(MethodForm):
    """Let staff switch the current web session to another user account."""

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_User('as_user').not_null())
        super().gdo_create_form(form)

    def gdo_render_title(self) -> str:
        return self.t('mt_admin_login_as', ())

    def get_as_user(self) -> GDO_User:
        return self.param_value('as_user')

    async def form_submitted(self):
        admin = self._env_user
        user = self.get_as_user()
        await user.authenticate(self._env_session)
        self.notify_login_as(user, admin)
        return self.redirect(Application.config('core.web_root'))

    @staticmethod
    def notify_login_as(user: GDO_User, admin: GDO_User) -> None:
        if not user.get_mail() or not module_enabled('mail'):
            return
        from gdo.mail.Mail import Mail
        lang = user.get_lang_iso()
        args = (user.render_name(), admin.render_name(), Application.config('core.sitename'))
        Mail.from_bot().subject(Trans.tiso(lang, 'mails_admin_login_as')).body(
            Trans.tiso(lang, 'mailb_admin_login_as', args)
        ).send_to_user(user)
