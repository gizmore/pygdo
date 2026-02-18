from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.Util import Files
from gdo.core.GDT_List import GDT_List
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.language.GDT_Trans import GDT_Trans
from gdo.message.GDT_HTML import GDT_HTML
from gdo.message.GDT_PRE import GDT_PRE
from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.GDT_Title import GDT_Title


class configure(MethodForm):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        module = self.get_module()
        form.text_raw(module.get_description())
        form.add_field(
            module.column('module_priority')
        )
        form.add_fields(*module.module_config().values())
        super().gdo_create_form(form)

    def form_submitted(self):
        module = self.get_module()
        for gdt in module.module_config().values():
            old = gdt.get_prev()
            new = gdt.get_val()
            if old != new:
                gdt._val = 1
                module.save_config_val(gdt.get_name(), new)
                self.msg('msg_module_conf_changed', (module.render_name(), gdt.get_name(), Render.italic(gdt.display_val(old)), Render.italic(gdt.display_val(new))))
        return self.render_page()

    def gdo_render_title(self) -> str:
        return t('mt_admin_configure', (self.get_module().render_name(),))

    def render_page(self):
        bar = GDT_Bar().vertical()
        module = self.get_module()
        installed = 'installed' if module.is_enabled() else 'not_installed'
        bar.add_fields(
            GDT_Title('mt').text('mt_admin_configure', (module.render_name(),)),
            GDT_Trans().text(installed),
            GDT_PRE().add_field(GDT_HTML().html(self.get_module_descr())),
            GDT_Menu().add_fields(GDT_List(module.gdo_admin_links())),
            self.get_form(),
            # installer,
        )
        return bar

    def get_module_descr(self) -> str:
        path = self.get_module().file_path('README.md')
        if not Files.is_file(path): return ''
        return Files.get_contents(path)
