import functools

from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.Util import html
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Field import GDT_Field
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm


class settings(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_render_title(self) -> str:
        return t('mt_account_settings', (self.get_module().render_name(),))

    def gdo_render_descr(self) -> str:
        return t('md_account_settings', ('OOPS',))

    @functools.cache
    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null().enabled(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        module = self.get_module()
        form.text('md_account_settings', (module.render_name(),))
        for gdt in module.all_user_settings():
            if not gdt.is_secret() or self._env_user.is_staff():
                if gdt2 := GDO_UserSetting.setting_column(gdt.get_name(), GDO_User.current()):
                    form.add_field(gdt2)
                else:
                    form.add_field(gdt)
        form.href(href('account', 'all_settings', f'&module={module.get_name}'))
        form.actions().add_field(GDT_Submit(f'submit_{module.get_name}').calling(self.form_submitted))

    def form_submitted(self):
        user = self._env_user
        module = self.get_module()
        out = []
        for gdt in module._all_user_settings():
            if gdt.is_writable():
                key = gdt.get_name()
                self.init_parameter(gdt)
                if gdt.get_val() != gdt._prev:
                    old = gdt._prev
                    new = gdt.get_val()
                    gdt.val(old)
                    user.save_setting(key, new)
                    gdt.val(new)
                    out.append(t('setting_changed', (key, Render.italic(html(str(old)), self._env_mode), Render.italic(html(str(new)), self._env_mode))))
        if len(out):
            self.msg('msg_settings_changed', (" ".join(out),))
        return self.render_page()
