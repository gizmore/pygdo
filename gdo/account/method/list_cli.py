from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.Connector import Connector
from gdo.core.GDO_UserSetting import GDO_UserSetting


class list_cli(Method):

    def gdo_trigger(self) -> str:
        return 'settings'

    def gdo_parameters(self) -> list[GDT]:
        return [
        ]

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_execute(self) -> GDT:
        user = self._env_user
        loader = ModuleLoader.instance()
        vals = {}
        for module in loader.enabled():
            for gdt in module.gdo_user_settings():
                gdt = GDO_UserSetting.setting_column(gdt.get_name(), user)
                vals[gdt.get_name()] = f"{gdt.get_name()}({gdt.render_val()})"
        sorted_vals = [vals[key] for key in sorted(vals.keys())]  # Get sorted values based on sorted keys
        return self.reply('msg_cli_settings', [", ".join(sorted_vals)])
