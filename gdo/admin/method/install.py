from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.util.href import href
from gdo.form.GDT_CSRF import GDT_CSRF
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.form.MethodForm import MethodForm
from gdo.install.Installer import Installer


class install(MethodForm):

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_create_form(self, form: GDT_Form) -> None:
        module = self.get_module()
        installed = module.installed()
        enabled = module.is_enabled()
        form.actions().add_fields(
            self.action('install', self.install, False),
            self.action('wipe', self.wipe, not installed),
            self.action('enable', self.enable, not installed or enabled),
            self.action('disable', self.disable, not installed or not enabled),
        )
        form.add_field(GDT_CSRF())

    def action(self, name: str, call: callable, disabled: bool) -> GDT_Submit:
        button = GDT_Submit(name).text(name).calling(call)
        return button.attr('disabled', 'disabled') if disabled else button

    async def install(self):
        await Installer.install_modules([self.get_module()])
        return self.redirect_module('msg_module_installed')

    async def wipe(self):
        Installer.wipe(self.get_module())
        return self.redirect_module('msg_module_wiped')

    async def enable(self):
        self.get_module().save_val('module_enabled', '1')
        return self.redirect_module('msg_module_enabled')

    async def disable(self):
        self.get_module().save_val('module_enabled', '0')
        return self.redirect_module('msg_module_disabled')

    def redirect_module(self, message: str):
        module = self.get_module()
        return self.redirect_msg(href('admin', 'module', f'&module={module.get_name}'), message)
