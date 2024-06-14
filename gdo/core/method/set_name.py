from gdo.base.GDT import GDT
from gdo.base.Util import html
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserName import GDT_UserName
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Validator import GDT_Validator
from gdo.form.MethodForm import MethodForm


class set_name(MethodForm):

    def gdo_trigger(self) -> str:
        return 'setname'

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_UserName('name').not_null(),
            GDT_Validator().validator(form, 'name', self.validate_name),
        )
        super().gdo_create_form(form)

    def validate_name(self, form: GDT_Form, field: GDT, value: any):
        my_id = self._env_user.get_id()
        count = GDO_User.table().count_where(f"user_name={GDT.quote(value)} AND user_id != {GDT.quote(my_id)}")
        if count:
            return field.error('err_username_taken')
        return True

    def form_submitted(self):
        name = self.param_val('name')
        self._env_user.save_val('user_displayname', name)
        return self.msg('msg_username_set', [html(name)])

