from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm
from gdo.install.Installer import Installer


class install(MethodForm):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Submit('install').calling(self.install))
        form.add_field(GDT_Submit('wipe').calling(self.wipe))
        form.add_field(GDT_CSRF())

    def install(self):
        Installer.install_module(self.get_module())
        return self.msg('msg_module_installed')

    def wipe(self):
        Installer.wipe(self.get_module())
        return self.msg('msg_module_wiped')

