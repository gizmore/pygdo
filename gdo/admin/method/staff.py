from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class staff(MethodForm):
    """
    Request admin permissions on a server.
    """

    def gdo_trigger(self) -> str:
        return "super"

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_create_form(self, form: GDT_Form) -> None:
        super().gdo_create_form(form)
