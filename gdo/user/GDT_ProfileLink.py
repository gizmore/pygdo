from gdo.base.Util import href
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Link import GDT_Link


class GDT_ProfileLink(GDT_Link):
    _user: GDO_User
    _with_username: bool
    _with_avatar: bool

    def __init__(self):
        super().__init__()
        self._with_avatar = False
        self._with_username = False

    def user(self, user: GDO_User):
        self._user = user
        self.href(href('user', 'profile', f'&for={user.get_id()}'))
        return self

    def with_username(self, with_username: bool = True):
        self._with_username = with_username
        self.text('%s', [self._user.render_name()])
        return self

    def with_avatar(self, with_avatar: bool = True):
        self._with_avatar = with_avatar
        return self


