from gdo.base.Trans import t, sitename
from gdo.base.util.href import url
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.mail.GDT_Email import GDT_Email
from gdo.mail.Mail import Mail
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.register.GDO_UserActivation import GDO_UserActivation
from gdo.ui.GDT_Link import GDT_Link


class change_mail(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'mail.change'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_Email('new_email').not_null(),
        )
        super().gdo_create_form(form)

    def form_submitted(self):
        """Confirm ownership of the new address before replacing the old one.

        Reuse the established registration activation records and endpoint;
        this keeps email confirmation tokens in one place rather than creating
        a second, subtly different token implementation.
        """
        user = self._env_user.get_effective_user()
        new_email = self.param_val('new_email')
        old_email = user.get_mail()
        if new_email == old_email:
            return self.error('err_mail_unchanged')

        # One pending address per account is enough.  A later request revokes
        # the earlier confirmation link.
        activation_table = GDO_UserActivation.table()
        activation_table.delete_where(
            "ua_username=%s AND ua_server=%s AND ua_password IS NULL" % (
                activation_table.quote(user.get_name()),
                activation_table.quote(user.get_server_id()),
            ))
        activation = GDO_UserActivation.blank({
            'ua_username': user.get_name(),
            'ua_server': user.get_server_id(),
            'ua_email': new_email,
            # Store JSON text: it remains directly hashable before MySQL has
            # round-tripped the activation object and is deserialised exactly
            # like the normal registration payload.
            'ua_data': GDT_Serialize('ua_data').to_val(
                {'mail_change_user': user.get_id()}).decode(),
        }).insert()

        if old_email:
            Mail.from_bot().recipient(old_email, user.get_displayname()).subject(
                t('mails_change_mail_requested')).body(
                t('mailb_change_mail_requested', (user.get_displayname(), new_email, sitename()))).send()

        link = GDT_Link().href(url('register', 'activate',
            f"&id={activation.get_id()}&token={activation.gdo_hash()}"))
        Mail.from_bot().recipient(new_email, user.get_displayname()).subject(
            t('mails_change_mail')).body(t('mailb_change_mail', (
                user.get_displayname(), sitename(), link.render_html(),
                f"$activate {activation.get_id()} {activation.gdo_hash()}",
            ))).send()
        return self.msg('msg_change_mail_requested')
