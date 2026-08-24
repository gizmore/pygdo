from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.base.Util import Arrays
from gdo.core.GDT_String import GDT_String


class whoami(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "whoami"

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        u = self._env_user
        reply_to = self._env_reply_to or u
        ps = []
        for p in u.permissions():
            ps.append(p)

        # Linked accounts execute as their master, but `whoami` should still
        # identify the connector account which actually sent the message.
        authed = 'authenticated' if reply_to._authenticated else 'not_authenticated'
        if reply_to.get_id() != u.get_id():
            origin = f"{reply_to.gdo_val('user_displayname')}{{{reply_to.get_server().get_name().lower()}}}"
            text = t('info_who_am_i_linked', (
                origin, t(authed), u.render_name(), Arrays.human_join(ps)))
            return GDT_String('result').val(text)
        text = t('info_who_am_i', (reply_to.render_name(), t(authed), Arrays.human_join(ps)))
        return GDT_String('result').val(text)
