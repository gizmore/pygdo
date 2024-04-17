from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit


class MethodForm(Method):
    _form: GDT_Form

    def gdo_parameters(self) -> [GDT]:
        return []

    def __init__(self):
        super().__init__()

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_CSRF())
        form.actions().add_field(GDT_Submit().calling(self.gdo_execute))

    def get_form(self) -> GDT_Form:
        if not hasattr(self, '_form'):
            self._form = GDT_Form()
            self.gdo_create_form(self._form)
            self.apply_input(self._form, self._input)
        return self._form

    def execute(self):
        if not super().prepare():
            return self
        form = self.get_form()
        for button in form.actions().fields():
            if isinstance(button, GDT_Submit) and self.has_input(button.get_name()):
                if form.validate(None):
                    return button.call()
        return form

    def gdo_execute(self):
        return self.get_form()

    def apply_input(self, gdt: GDT, input_: dict):
        if gdt.is_writable():
            gdt.val(input_.get(gdt.get_name()))
        for gdt2 in gdt.fields():
            self.apply_input(gdt2, input_)

