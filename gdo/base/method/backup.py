from gdo.core.GDT_Path import GDT_Path
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class backup(MethodForm):

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Path('to').existing_dir().writable())
        super().gdo_create_form(form)

    def form_submitted(self):
        return self.msg('msg_backup_completed')
    