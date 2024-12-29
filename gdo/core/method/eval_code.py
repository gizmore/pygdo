from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm

class eval_code(MethodForm):

    def gdo_trigger(self) -> str:
        return 'eval'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_RestOfText('expression').not_null())
        super().gdo_create_form(form)

    def get_expression(self) -> str:
        return self.param_value('expression')

    def form_submitted(self):
        return self.empty(str(eval(self.get_expression())))
