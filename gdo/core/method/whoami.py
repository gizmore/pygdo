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
        ps = []
        for p in u.permissions():
            ps.append(p)

        authed = 'authenticated' if u._authenticated else 'not_authenticated'
        text = t('info_who_am_i', (u.render_name(), t(authed), Arrays.human_join(ps)))
        return GDT_String('result').val(text)
