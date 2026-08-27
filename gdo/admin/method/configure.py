from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.UserTemp import UserTemp
from gdo.base.util.href import href
from gdo.core.GDT_List import GDT_List
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.language.GDT_Trans import GDT_Trans
from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.GDT_Success import GDT_Success
from gdo.ui.GDT_Title import GDT_Title


class configure(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        module = self.get_module()
        form.text_raw(module.get_description())
        form.add_field(module.column('module_sort'))
        form.add_fields(*module.module_config().values())
        super().gdo_create_form(form)

    async def form_submitted(self):
        module = self.get_module()
        changes = []
        module_sort = self.get_form().get_field('module_sort')
        old = module_sort.get_prev()
        new = module_sort.get_val()
        if old != new:
            module.save_val('module_sort', new)
            changes.append((module.render_name(), module_sort.get_name(), Render.italic(module_sort.display_var(old)), Render.italic(module_sort.display_var(new))))
        for gdt in module.module_config().values():
            old = gdt.get_prev()
            new = gdt.get_val()
            if old != new:
                await module.save_config_val(gdt.get_name(), new, True)
                changes.append((module.render_name(), gdt.get_name(), Render.italic(gdt.display_var(old)), Render.italic(gdt.display_var(new))))
        for change in changes:
            UserTemp.flash(self._env_user, GDT_Success().title_raw(module.render_name()).text('msg_module_conf_changed', change))
        return self.redirect(href('admin', 'module', f'&module={module.get_name}'))

    def gdo_render_title(self) -> str:
        return t('mt_admin_configure', (self.get_module().render_name(),))

    def render_page(self):
        bar = GDT_Bar().vertical()
        module = self.get_module()
        installed = 'installed' if module.is_enabled() else 'not_installed'
        bar.add_fields(
            GDT_Menu().add_fields(GDT_List(*module.gdo_admin_links())),
            GDT_Title('mt').text('mt_admin_configure', (module.render_name(),)),
            GDT_Trans().text(installed),
            self.get_form(),
        )
        return bar
