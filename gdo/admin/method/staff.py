from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class staff(MethodForm):
    """
    Request staff permissions on a server.
    """

    def gdo_trigger(self) -> str:
        return "staff"

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_create_form(self, form: GDT_Form) -> None:
        super().gdo_create_form(form)
