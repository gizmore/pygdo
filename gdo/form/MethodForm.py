from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.GDO import GDO
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.base.Util import module_enabled
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit


class MethodForm(Method):
    _form: GDT_Form

    __slots__ = (
        '_form',
    )

    def gdo_parameters(self) -> list[GDT]:
        return GDO.EMPTY_LIST

    def gdo_captcha(self) -> bool:
        return False

    def gdo_submit_button(self) -> GDT_Submit:
        return GDT_Submit().calling(self.form_submitted).default_button()

    def gdo_create_form(self, form: GDT_Form) -> None:
        self.create_default_form_elements(form)

    def create_default_form_elements(self, form: GDT_Form) -> None:
        if Application.IS_HTTP:
            form.add_field(GDT_CSRF())
        if self.gdo_captcha() and module_enabled('captcha'):
            from gdo.captcha.GDT_Captcha import GDT_Captcha
            form.add_field(GDT_Captcha())
        form.actions().add_field(self.gdo_submit_button())

    def get_form(self, reset: bool = False) -> GDT_Form:
        # if reset:
        #     delattr(self, '_parameters')
        if not hasattr(self, '_form'): # or reset:
            self._form = GDT_Form().href(self.href()).method(self).title_raw(self.gdo_render_title())
            self.gdo_create_form(self._form)
            # self.parameters()
        return self._form

    def gdo_execute(self) -> GDT:
        self.parameters()
        form = self.get_form()

        ### Flow upload
        if key := self._raw_args.args.get('flowField'):
            return form.get_field(key).flow_upload()

        clicked = None
        for button in form.actions().fields():
            if button._default_button and not Application.IS_HTTP:
                clicked = button
            if isinstance(button, GDT_Submit) and button.get_val():
                clicked = button
                break
        if clicked:
            if form.validate(None):
                return clicked.call()
            else:
                return self.form_invalid()
        return self.render_page()

    def render_page(self) -> GDT:
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
        self.err('err_form_invalid', (" ".join(errors),))
        if not Application.is_html():
            self.err('%s', ('\n' + self.render_cli_usage(),))
        return self.get_form()

    def parameters(self, reset: bool = False) -> dict[str,GDT]:
        if hasattr(self, '_parameters') and not reset:
            return self._parameters
        params = super().parameters(reset)
        for gdt in self.form_parameters():
            self.init_parameter(gdt)
        return params

    def form_parameters(self) -> list[GDT]:
        yield from self.get_form().all_fields()
        yield from self.get_form().actions().all_fields()

    def cli_auto_button(self):
        for gdt in self.get_form().actions().all_fields():
            if isinstance(gdt, GDT_Submit) and gdt._default_button:
                self._raw_args.add_arg(gdt.get_name(), '1')
                break
        return self

    def clear_form(self):
        self._raw_args.clear()
        for gdt in self.parameters().values():
            gdt.val(gdt.get_initial())
