from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String
from gdo.core.GDO_User import GDO_User
from gdo.core.UserLinkToken import UserLinkToken


class approve(Method):
    """Accept a signed request from the exact connector account."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'user.approve'

    def gdo_needs_authentication(self) -> bool:
        return True

    def gdo_parameters(self):
        return [GDT_String('token').ascii().maxlen(192).not_null()]

    def gdo_execute(self):
        token = self.param_val('token')
        ids = UserLinkToken.parse(token)
        if ids is None:
            return self.empty('This account connection token is invalid or has expired.')
        master_id, slave_id = ids

        # A dispatched message has already switched env_user to the master.
        # Its retained reply identity proves control of the slave account.
        message = getattr(self, '_message', None)
        origin = self._env_user
        if int(origin.get_id()) != slave_id:
            origin = getattr(message, '_env_reply_to', None) or origin
        if slave_id != int(origin.get_id()):
            return self.empty('This account connection belongs to another account.')
        slave = GDO_User.table().get_by_id(str(slave_id))
        master = GDO_User.table().get_by_id(str(master_id))
        if slave is None or master is None:
            return self.empty('This account connection refers to an unknown account.')
        if slave.get_linked_user():
            return self.empty('This account is already linked.')
        if master.get_effective_user().get_id() != master.get_id():
            return self.empty('A linked account cannot become a link master.')
        slave.save_val('user_link', master.get_id())
        return self.empty(f'{slave.render_name()} now uses {master.render_name()} as its connected account.')
