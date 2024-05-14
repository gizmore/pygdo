from gdo.base.Trans import t
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.math.GDT_MathExpression import GDT_MathExpression


class calc(MethodForm):
    LAST_RESULT = {}

    def gdo_render_descr(self) -> str:
        return t('md_math_calc', [self.render_allowed_functions()])

    def render_allowed_functions(self) -> str:
        values = list(GDT_MathExpression('expression').get_namespace().keys())
        return ', '.join(values)

    def gdo_trigger(self) -> str:
        return 'calc'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.text('md_math_calc', [self.render_allowed_functions()])
        form.add_field(GDT_MathExpression('expression').not_null())
        super().gdo_create_form(form)

    def form_submitted(self):
        gdt = self.parameters()['expression']
        expr = gdt.get_val().lower().replace('_', self.last_value())
        result = eval(expr, GDT_MathExpression('x').get_namespace())
        self.LAST_RESULT[self._env_user] = result
        self.msg('%s', [result])
        return self.render_page()

    def last_value(self):
        if self._env_user not in self.LAST_RESULT:
            self.LAST_RESULT[self._env_user] = 0
        return self.LAST_RESULT[self._env_user]
