from gdo.base.Trans import t
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Link import GDT_Link


class GDT_ProfileLink(GDT_Link):
    _user: GDO_User
    _with_username: bool
    _with_avatar: bool

    def __init__(self, name: str=None):
        super().__init__(name)
        self._with_avatar = False
        self._with_username = False

    def gdo(self, gdo: 'GDO'):
        return self.user(gdo)

    def user(self, user: GDO_User, with_username: bool = True):
        self._user = user
        self.href(href('user', 'profile', f'&for={user.get_id()}'))
        return self.with_username(with_username)

    def with_username(self, with_username: bool = True):
        self._with_username = with_username
        self.text('%s', (self._user.render_name(),))
        return self

    def with_avatar(self, with_avatar: bool = True):
        self._with_avatar = with_avatar
        return self

    def render_label(self) -> str:
        return t('profile')