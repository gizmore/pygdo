from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import module_enabled
from gdo.base.WithRateLimit import WithRateLimit
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.ui.GDT_Card import GDT_Card


class profile(Method):

    def gdo_trigger(self) -> str:
        return 'profile'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_User('for').not_null(),
        ]

    def get_user(self) -> GDO_User:
        return self.param_value('for')

    def gdo_execute(self) -> GDT:
        user = self.get_user()
        card = GDT_Card()
        if module_enabled('avatar'):
            from gdo.avatar.GDT_Avatar import GDT_Avatar
            card.image(GDT_Avatar('avatar').for_user(user))
        card.title('whose_profile', (user.render_name(),))
        return card
