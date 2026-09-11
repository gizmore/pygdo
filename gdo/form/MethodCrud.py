from abc import abstractmethod

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Object import GDT_Object
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm


class MethodCrud(MethodForm):
    """Small create/update form base for one GDO table.

    Subclasses choose the table and the writable fields.  This deliberately
    leaves permission policy and structural changes to the concrete method.
    """

    @abstractmethod
    def gdo_table(self) -> GDO:
        raise NotImplementedError

    def crud_name(self) -> str:
        return 'id'

    def feature_create(self) -> bool:
        return True

    def feature_update(self) -> bool:
        return True

    def feature_delete(self) -> bool:
        return True

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Object(self.crud_name()).table(self.gdo_table())]

    def gdo_form_fields(self, gdo: GDO) -> list[GDT]:
        return [
            column.gdo(gdo)
            for column in gdo.columns().values()
            if not column.is_primary() and column.is_writable()
        ]

    def crud_gdo(self) -> GDO | None:
        return self.param_value(self.crud_name(), False)

    def gdo_create_form(self, form: GDT_Form) -> None:
        gdo = self.crud_gdo()
        target = gdo or self.gdo_table()
        form.add_fields(*self.gdo_form_fields(target))
        if gdo and self.feature_update():
            form.actions().add_field(self.crud_edit_button())
            if self.feature_delete():
                form.actions().add_field(self.crud_delete_button())
        elif not gdo and self.feature_create():
            form.actions().add_field(self.crud_create_button())

    def crud_create_button(self) -> GDT_Submit:
        return GDT_Submit('create').text_raw('Create').calling(self.on_create).default_button()

    def crud_edit_button(self) -> GDT_Submit:
        return GDT_Submit('edit').text_raw('Edit').calling(self.on_update).default_button()

    def crud_delete_button(self) -> GDT_Submit:
        return GDT_Submit('delete').text_raw('Delete').calling(self.on_delete)

    def form_values(self) -> dict[str, str]:
        return {
            field.get_name(): field.get_val()
            for field in self.gdo_form_fields(self.crud_gdo() or self.gdo_table())
        }

    def on_create(self):
        gdo = self.gdo_table().blank(self.form_values()).insert()
        self.msg('msg_crud_created', (gdo.render_name(),))
        return self.get_form()

    def on_update(self):
        gdo = self.crud_gdo()
        gdo.save_vals(self.form_values())
        self.msg('msg_crud_updated', (gdo.render_name(),))
        return self.get_form()

    def on_delete(self):
        gdo = self.crud_gdo()
        name = gdo.render_name()
        gdo.delete()
        self.msg('msg_crud_deleted', (name,))
        return self.get_form()
