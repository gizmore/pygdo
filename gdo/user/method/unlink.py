from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Connector import Connector
from gdo.core.GDT_Bool import GDT_Bool


class unlink(Method):
    """Remove the invoking connector account's link to its master account."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'user.unlink'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_needs_authentication(self) -> bool:
        return True

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Bool('confirm')]

    def gdo_execute(self) -> GDT:
        # Message.execute changes _env_user to the effective account.  The
        # link belongs to the connector identity that actually invoked us.
        user = getattr(self, '_env_reply_to', None) or self._env_user
        master = user.get_linked_user()
        if not master:
            return self.err('err_user_unlink_not_linked')
        if not self.param_value('confirm'):
            return self.err('err_user_unlink_confirm')
        user.save_val('user_link', None)
        return self.reply('msg_user_unlinked', (user.render_name(), master.render_name()))
