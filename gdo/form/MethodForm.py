import functools

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
        form.actions().add_field(GDT_Submit().calling(self.form_submitted))

    def get_form(self) -> GDT_Form:
        if not hasattr(self, '_form'):
            self._form = GDT_Form()
            self.gdo_create_form(self._form)
            # self.apply_input(self._form, self._input)
        return self._form

    # def execute(self):
    #     if not super().prepare():
    #         return self

    def gdo_execute(self):
        form = self.get_form()
        for button in form.actions().fields():
            if isinstance(button, GDT_Submit) and button.get_val():
                if form.validate(None):
                    return button.call()
                else:
                    return self.form_invalid()
        return self.render_page()

    def render_page(self):
        return self.get_form()

    def form_submitted(self):
        form = self.get_form()
        self.msg('msg_form_submitted')
        return form

    def form_invalid(self):
        form = self.get_form()
        errors = []
        for gdt in form.all_fields():
            if gdt.has_error():
                errors.append(f"{gdt.get_name()}: {gdt.render_error()}")
        self.err('err_form_invalid', ["\n".join(errors)])
        return self.get_form()

    # def apply_input(self, gdt: GDT, input_: dict):
    #     if gdt.is_writable():
    #         gdt.val(input_.get(gdt.get_name()))
    #     for gdt2 in gdt.fields():
    #         self.apply_input(gdt2, input_)

    # def param_val(self, key: str, throw: bool = True):
    #     for gdt in self.get_form().all_fields():
    #         if gdt.get_name() == key:
    #             return gdt.get_val()
    #     return super().param_val(key)
    #
    # def param_value(self, key: str, throw: bool = True):
    #     for gdt in self.get_form().all_fields():
    #         if gdt.get_name() == key:
    #             return gdt.to_value(gdt.get_val())
    #     return super().param_value(key)

    @functools.cache
    def parameters(self) -> dict[str, GDT]:
        if hasattr(self, '_parameters'):
            return self._parameters
        params = super().parameters()
        for gdt in self.get_form().all_fields():
            params[gdt.get_name()] = gdt
        for gdt in self.get_form().actions().all_fields():
            params[gdt.get_name()] = gdt
        return params
