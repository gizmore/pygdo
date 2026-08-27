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
            return self.err('err_user_already_linked')
        if slave.get_linked_user():
            return self.empty('err_user_different_link')
        token = UserLinkToken.create(master, slave)
        return self.msg('msg_user_link_request', (slave.render_name(), f'$user.approve {token}'))
