from gdo.base.Trans import t
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.math.GDT_MathExpression import GDT_MathExpression


class calc(MethodForm):
    LAST_RESULT = {}

    def gdo_render_descr(self) -> str:
        return t('md_math_calc', (self.render_allowed_functions(),))

    def render_allowed_functions(self) -> str:
        values = [key for key in GDT_MathExpression('x').get_namespace() if key not in ('for', 'in')]
        return ', '.join(values)

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'calc'

    def gdo_permission(self):
        return 'voice'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.text('md_math_calc', (self.render_allowed_functions(),))
        form.add_field(GDT_MathExpression('expression').not_null())
        super().gdo_create_form(form)

    def form_submitted(self):
        expr = self.param_value('expression').lower().replace('_', self.last_value())
        result = str(eval(expr, {'__builtins__': {}}, self.parameter('expression').get_namespace()))
        self.LAST_RESULT[self._env_user] = result
        return self.empty(str(result))

    def last_value(self):
        if self._env_user not in self.LAST_RESULT:
            self.LAST_RESULT[self._env_user] = "0"
        return self.LAST_RESULT[self._env_user]
