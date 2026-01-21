from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.mail.GDT_Email import GDT_Email


class change_mail(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'mail.change'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_Email('new_email').not_null(),
        )
        super().gdo_create_form(form)

    def form_submitted(self):
        pass