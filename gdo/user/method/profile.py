from gdo.base.GDT import GDT
from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t, sitename
from gdo.base.Util import module_enabled
from gdo.base.WithRateLimit import WithRateLimit
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_User import GDT_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.ui.GDT_Card import GDT_Card
from gdo.ui.GDT_Menu import GDT_Menu


class profile(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'profile'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('for').not_null(),
        ]

    def get_user(self) -> GDO_User:
        return self.param_value('for')

    def gdo_render_title(self) -> str:
        return t('mt_user_profile', (self.get_user().render_name(),))

    def gdo_render_descr(self) -> str:
        return t('md_user_profile', (self.get_user().render_name(), sitename()))

    def gdo_execute(self) -> GDT:

        user = self.get_user()
        if user != self._env_user:
            user.increase_setting('profile_views')
        modules = ModuleLoader.instance().enabled()
        # A profile can show settings from many modules.  Prime the target
        # user's values once, rather than issuing one query per setting.
        GDO_UserSetting.load_for_user(user)
        card = GDT_Card()
        profile_links = GDT_Menu().vertical()
        if module_enabled('avatar'):
            from gdo.avatar.GDT_Avatar import GDT_Avatar
            profile_links.add_field(GDT_Avatar('avatar').for_user(user).add_class('gdo-avatar-profile img-fluid rounded-start'))
        Application.EVENTS.publish_sync('user_profile_links', user, profile_links)
        if profile_links.all_fields():
            card.image(profile_links)
        card.title('mt_user_profile', (user.render_name(),))
        content = card.get_content()
        content.add_field(user.column('user_name'))
        content.add_field(user.column('user_displayname'))
        content.add_field(user.column('user_server'))
        for module in modules:
            for gdt in module.gdo_profile_links(user):
                if isinstance(gdt, GDT_Field) and not gdt.is_hidden():
                    content.add_field(gdt)
        for module in modules:
            for gdt in (*module.gdo_user_settings(), *module.gdo_user_config()):
                if isinstance(gdt, GDT_Field):
                    if setting := GDO_UserSetting.setting_column(gdt.get_name(), user):
                        if setting.get_val() is not None and not setting.is_secret() and not setting.is_hidden():
                            content.add_field(setting)
        return card
