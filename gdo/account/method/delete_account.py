from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Trans import Trans, t
from gdo.base.Util import Strings, module_enabled
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Text import GDT_Text
from gdo.date.Time import Time
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm


class delete_account(MethodForm):
    """Let an authenticated user disable or permanently prune their account."""

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'

    def gdo_render_title(self) -> str:
        return t('mt_account_delete_account')

    def gdo_render_descr(self) -> str:
        return t('md_account_delete_account')

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.text('md_account_delete_account')
        form.add_fields(
            GDT_Text('reason'),
            GDT_Bool('confirm').not_null().label('confirm_account_delete'),
            GDT_CSRF(),
        )
        form.actions().add_fields(
            self.action('disable', self.disable, 'confirm_account_disable'),
            self.action('prune', self.prune, 'confirm_account_prune'),
        )

    @staticmethod
    def action(name: str, call: callable, question_key: str) -> GDT_Submit:
        return GDT_Submit(name).text(name).calling(call).attr(
            'onclick', f'return window.confirm({json.dumps(t(question_key))})'
        )

    def is_confirmed(self) -> bool:
        if self.param_value('confirm'):
            return True
        self.err('err_account_delete_confirm')
        return False

    def get_reason(self) -> str:
        return self.param_val('reason') or ''

    async def disable(self) -> GDT:
        if not self.is_confirmed():
            return self.get_form()
        await self.disable_user(self._env_user, self.get_reason())
        return self.redirect(Application.config('core.web_root'), 'msg_account_disabled')

    async def prune(self) -> GDT:
        if not self.is_confirmed():
            return self.get_form()
        await self.prune_user(self._env_user, self.get_reason())
        return self.redirect(Application.config('core.web_root'), 'msg_account_pruned')

    async def disable_user(self, user: GDO_User, reason: str = '') -> None:
        user.save_setting('deleted', Time.get_date())
        self.send_staff_mail(user, 'disabled', reason)
        await user.logout(self._env_session)

    async def prune_user(self, user: GDO_User, reason: str = '') -> None:
        self.send_staff_mail(user, 'pruned', reason)
        # End this request's authenticated state. The sess_user foreign key
        # cascades all persisted sessions when the account is removed below.
        await user.logout(self._env_session)
        user.delete()

    @staticmethod
    def send_staff_mail(user: GDO_User, action: str, reason: str) -> None:
        if not module_enabled('mail'):
            return
        from gdo.mail.Mail import Mail
        for staff in GDO_User.staff():
            if not staff.get_mail():
                continue
            lang = staff.get_lang_iso()
            body = Trans.tiso(lang, 'mailb_account_delete', (
                user.render_name(),
                Trans.tiso(lang, f'account_delete_{action}'),
                Strings.html(reason) if reason else Trans.tiso(lang, 'none'),
            ))
            Mail.from_bot().subject(Trans.tiso(lang, 'mails_account_delete')).body(body).send_to_user(staff)
import json
