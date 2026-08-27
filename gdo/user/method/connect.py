from gdo.core.GDT_User import GDT_User
from gdo.core.UserLinkToken import UserLinkToken
from gdo.form.MethodForm import MethodForm


class connect(MethodForm):
    """Create a short-lived approval token for connecting another account."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'user.connect'

    def gdo_needs_authentication(self) -> bool:
        return True

    def gdo_parameters(self):
        return [GDT_User('slave').not_null()]

    def gdo_create_form(self, form):
        form.add_field(self.parameters()['slave'])
        super().gdo_create_form(form)

    def form_submitted(self):
        master = self._env_user
        slave = self.param_value('slave')
        if slave.get_id() == master.get_id() or slave.get_effective_user().get_id() == master.get_id():
            return self.empty('This account is already linked to you.')
        if slave.get_linked_user():
            return self.empty('This account is already linked. Unlink it before creating a new request.')
        token = UserLinkToken.create(master, slave)
        return self.empty(
            f'Ask {slave.render_name()} to send: $user.approve {token}')
