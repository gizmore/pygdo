from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t, sitename
from gdo.base.Util import module_enabled
from gdo.base.WithRateLimit import WithRateLimit
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.ui.GDT_Card import GDT_Card


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
        card = GDT_Card()
        if module_enabled('avatar'):
            from gdo.avatar.GDT_Avatar import GDT_Avatar
            card.image(GDT_Avatar('avatar').for_user(user))
        card.title('whose_profile', (user.render_name(),))
        content = card.get_content()
        for module in ModuleLoader.instance().enabled():
            for gdt in module.all_user_settings():
                if gdt := GDO_UserSetting.setting_column(gdt.get_name(), GDO_User.current()):
                    if isinstance(gdt, GDT_Field):
                        content.add_field(gdt)
        return card
