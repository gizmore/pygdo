from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.base.Util import Arrays
from gdo.core.GDT_String import GDT_String


class whoami(Method):

    def gdo_trigger(self) -> str:
        return "whoami"

    def gdo_execute(self) -> GDT:
        u = self._env_user
        ps = []
        for p in u.permissions():
            ps.append(p)

        text = t('info_who_am_i', [u.render_name(), Arrays.human_join(ps)])
        return GDT_String('result').val(text)
