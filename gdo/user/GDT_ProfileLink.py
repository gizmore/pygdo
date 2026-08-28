from gdo.base.Trans import t
from gdo.base.util.href import href
from gdo.base.Render import Mode
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Link import GDT_Link


class GDT_ProfileLink(GDT_Link):
    _user: GDO_User
    _with_username: bool
    _with_avatar: bool

    def __init__(self, name: str=None):
        super().__init__(name)
        # A profile name is already a clear navigation affordance. Unlike a
        # generic GDT_Link it should not prepend the generic link glyph.
        del self._icon_name
        self._with_avatar = False
        self._with_username = False

    def gdo(self, gdo: 'GDO'):
        return self.user(gdo)

    def user(self, user: GDO_User, with_username: bool = True):
        self._user = user
        self.href(href('user', 'profile', f'&for={user.get_id()}-{user.get_name_sid()}'))
        self.attr('title', f"{t('level')}: {user.get_setting_val('level')} | {t('score')}: {user.get_setting_val('score')}")
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

    def render_html(self) -> str:
        content = ''
        if self._with_avatar:
            gdt = self._user.gdt_user_settings().KNOWN.get('avatar_file')
            if gdt:
                content += gdt.for_user(self._user).render_html() + '&nbsp;'
        content += self.render_text()
        # The avatar and user name are one profile affordance: both must be
        # inside the anchor so clicking either opens the same profile.
        return f'<a class="gdt-link" href="{self.render_href()}"{self.html_attrs()}><span>{self.render_icon(Mode.render_html)}{content}</span></a>'
