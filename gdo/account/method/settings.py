from gdo.base.ModuleLoader import ModuleLoader
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.ui.GDT_Section import GDT_Section


class settings(MethodForm):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_create_form(self, form: GDT_Form) -> None:

        for module in ModuleLoader.instance()._cache:
            form.add_field(GDT_Section().title_raw(module.get_name()))
            for gdt in module.user_settings():
                form.add_field(gdt)




