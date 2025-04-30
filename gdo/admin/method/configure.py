from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


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
        for gdt in module._module_config.values():
            form.add_field(gdt)

        super().gdo_create_form(form)

    def form_submitted(self):
        return self.render_page()
