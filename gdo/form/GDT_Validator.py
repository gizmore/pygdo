from gdo.base.GDT import GDT
from gdo.base.Util import dump
from gdo.base.WithError import WithError
from gdo.form.GDT_Form import GDT_Form


class GDT_Validator(WithError, GDT):
    _validator_form: GDT_Form
    _validator_field: GDT
    _validator_func: callable

    def dummy_func(self, form: GDT_Form, field: GDT, value: any) -> bool:
        dump(form, field, value)
        return True

    def __init__(self):
        super().__init__()
        self._validator_func = self.dummy_func

    def validate_form_field(self, form: GDT_Form, field_name: str, validator: callable):
        self._validator_form = form
        self._validator_field = form.get_field(field_name)
        self._validator_func = validator
        return self

    def validate(self, value) -> bool:
        value = self._validator_field.get_value()
        if value is None:
            return True
        return self._validator_func(self._validator_form, self._validator_field, value)

