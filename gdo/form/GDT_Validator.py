from typing import Any, Callable
from gdo.base.WithError import WithError
from gdo.base.GDT import GDT
from gdo.form.GDT_Form import GDT_Form


class GDT_Validator(WithError, GDT):
    """
    Custom validator.
    Usage: GDT_Validator().validator(form, field_name_to_validate, callable)
    Callable: def func(self, form: GDT_Form, field: GDT, value: any) -> bool:
    """
    _validator_form: GDT_Form|None
    _validator_field: str
    _validator_func: Callable

    def dummy_func(self, form: GDT_Form, field: GDT, value: Any) -> bool:
        return field.error('err_validator_stub')

    def __init__(self):
        super().__init__()
        self._validator_func = self.dummy_func
        self._validator_field = ''
        self._validator_form = None

    def validator(self, form: GDT_Form|None, field_name: str, validator: Callable):
        self._validator_form = form
        self._validator_field = field_name
        self._validator_func = validator
        return self

    def validate(self, val: str|None) -> bool:
        form = self._validator_form
        gdt = form.get_field(self._validator_field)
        value = gdt.get_value()
        return self._validator_func(form, gdt, value)
