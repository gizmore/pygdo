from gdo.base.GDT import GDT
from gdo.base.Util import dump
from gdo.base.WithError import WithError
from gdo.form.GDT_Form import GDT_Form


class GDT_Validator(WithError, GDT):
    """
    Custom validator.
    Usage: GDT_Validator().validate(form, field_name, func)
    """
    _validator_form: GDT_Form
    _validator_field: str
    _validator_func: callable

    def dummy_func(self, form: GDT_Form, field: GDT, value: any) -> bool:
        dump(form, field, value)
        return True

    def __init__(self):
        super().__init__()
        self._validator_func = self.dummy_func

    def validator(self, form: GDT_Form, field_name: str, validator: callable):
        self._validator_form = form
        self._validator_field = field_name
        self._validator_func = validator
        return self

    def validate(self, val: str | None, value: any) -> bool:
        if value is None:
            return True
        form = self._validator_form
        gdt = form.get_field(self._validator_field)
        value = gdt.get_value()
        return self._validator_func(form, gdt, value)
