from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.base.Util import href
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm


class settings(MethodForm):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_render_title(self) -> str:
        return t('mt_account_settings', [self.get_module().render_name()])

    def gdo_render_descr(self) -> str:
        return t('md_account_settings', ['OOPS'])

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Module('module').not_null().enabled(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        module = self.get_module()
        form.text('md_account_settings', [module.render_name()])
        for gdt in module.all_user_settings():
            form.add_field(gdt)
        form.href(href('account', 'all_settings', f'&module={module.get_name()}'))
        form.actions().add_field(GDT_Submit(f'submit_{module.get_name()}').calling(self.form_submitted))
        # super().gdo_create_form(form)

    def form_submitted(self):
        user = self._env_user
        module = self.get_module()
        out = []
        for gdt in module.all_user_settings():
            key = gdt.get_name()
            self._nested_parse()
            if gdt.get_val() != gdt.get_initial():
                old = gdt.get_initial()
                new = gdt.get_val()
                gdt.val(old)
                user.save_setting(key, new)
                gdt.val(new)
                out.append(t('setting_changed', [key, old, new]))
        if len(out):
            self.msg('msg_settings_changed', [" ".join(out)])
        return self.render_page()

