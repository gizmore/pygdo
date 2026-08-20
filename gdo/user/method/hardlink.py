from gdo.core.GDT_User import GDT_User
from gdo.form.MethodForm import MethodForm


class hardlink(MethodForm):
    """Staff-only direct link from a master account to a chosen slave."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'user.hardlink'

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_needs_authentication(self) -> bool:
        return True

    def gdo_parameters(self):
        # A normal invocation is: $user.hardlink <slave>.
        # Staff can deliberately override the default current master with
        # --master=<user> when repairing a known account relationship.
        return [
            GDT_User('master').initial(str(self._env_user.get_id())),
            GDT_User('slave').not_null(),
        ]

    def gdo_create_form(self, form):
        form.add_field(self.parameters()['master'])
        form.add_field(self.parameters()['slave'])
        super().gdo_create_form(form)

    def form_submitted(self):
        master = self.param_value('master')
        slave = self.param_value('slave')
        if slave.get_id() == master.get_id():
            return self.empty('This account is already the chosen master.')
        if slave.get_linked_user():
            return self.empty('This connector account is already linked. Unlink it before changing its master.')
        if master.get_effective_user().get_id() != master.get_id():
            return self.empty('A linked account cannot become a link master.')
        slave.save_val('user_link', master.get_id())
        return self.empty(f'{slave.render_name()} now uses {master.render_name()} as its connected account.')
