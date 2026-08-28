from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Connector import Connector
from gdo.core.GDT_Bool import GDT_Bool
from gdo.install.Installer import Installer


class safe_install(Method):
    """Install one module from a text connector without destructive actions."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'safe.install'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_user_permission(self) -> str | None:
        return 'owner'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null().positional(),
            GDT_Bool('confirm'),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    async def gdo_execute(self):
        module = self.get_module()
        if module.installed():
            return self.err('err_safe_install_installed', (module.render_name(),))
        if not self.param_value('confirm'):
            return self.err('err_safe_install_confirm')
        await Installer.install_modules([module])
        return self.reply('msg_safe_install_done', (module.render_name(),))
