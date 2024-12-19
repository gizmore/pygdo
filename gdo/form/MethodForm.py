from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit


class MethodForm(Method):
    _form: GDT_Form

    def gdo_parameters(self) -> list[GDT]:
        return []

    def __init__(self):
        super().__init__()

    def gdo_create_form(self, form: GDT_Form) -> None:
        if Application.is_html():
            form.add_field(GDT_CSRF())
        form.actions().add_field(GDT_Submit().calling(self.form_submitted).default_button())

    def get_form(self, reset: bool = False) -> GDT_Form:
        if not hasattr(self, '_form') or reset:
            self._form = GDT_Form()
            self.gdo_create_form(self._form)
        if reset:
            delattr(self, '_parameters')
            self._nested_parse()
        return self._form

    async def gdo_execute(self) -> GDT:
        form = self.get_form()

        ### Flow upload
        if 'flowField' in self._args:
            return form.get_field(self._args['flowField']).flow_upload()

        for gdt in form.all_fields():
            await gdt.gdo_file_upload(self)

        for button in form.actions().fields():
            if isinstance(button, GDT_Submit) and button.get_val():
                if await form.validate(None, None):
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
                name = Render.red(Render.bold(gdt.get_name(), self._env_mode), self._env_mode)
                error = Render.red(gdt.render_error(), self._env_mode)
                errors.append(f"{name}: {error}")
        self.err('err_form_invalid', [" ".join(errors)])
        if not Application.is_html():
            self.err('%s', ['\n' + self.get_arg_parser(True).format_usage()])
        return self.get_form()

    def parameters(self, reset: bool = False) -> dict[str, GDT]:
        if hasattr(self, '_parameters') and not reset:
            return self._parameters
        params = super().parameters()
        self._nested_parse()
        for gdt in self.get_form().all_fields():
            params[gdt.get_name()] = gdt
        for gdt in self.get_form().actions().all_fields():
            params[gdt.get_name()] = gdt
        return params

    def cli_auto_button(self):
        for gdt in self.get_form().actions().all_fields():
            if isinstance(gdt, GDT_Submit) and gdt._default_button:
                self.arg(f'--{gdt.get_name()}')
                self.arg('1')
                break
        return self
