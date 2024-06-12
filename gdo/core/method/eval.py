from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class eval(MethodForm):

    def gdo_user_type(self) -> str | None:
        return 'admin'

    def gdo_create_form(self, form: GDT_Form) -> None:
        super().gdo_create_form(form)

    def form_submitted(self):
        return self
