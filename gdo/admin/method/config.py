from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import html
from gdo.core.Connector import Connector
from gdo.core.GDT_String import GDT_String


class config(Method):
    """
    Get the list of config, the list of config for a module, state of a config var or set a config var
    """

    def gdo_trigger(self) -> str:
        return "adm.conf"

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Module('module'),
            GDT_String('config_name'),
            GDT_String('config_value'),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_execute(self):
        module = self.get_module()
        if not module:
            return self.list_all()
        config_name = self.param_val('config_name')
        if not config_name:
            return self.list_module(module)
        gdt = module.config_column(config_name)
        if not gdt:
            return self.err('err_module_config_gdt', [html(config_name)])
        value = self.param_val('config_value')
        if not value:
            return self.show_value(module, gdt)
        value = None if value == "None" else value
        return self.set_value(module, gdt, value)

    def list_all(self):
        loader = ModuleLoader.instance()
        all = {}
        for module in loader._cache.values():
            name = module.render_name()
            if name not in all:
                all[name] = []

        return GDT_String('list').val("out")

    def list_module(self, module: GDO_Module):
        pass

    def show_value(self, module: GDO_Module, gdt: GDT):
        pass

    def set_value(self, module: GDO_Module, gdt: GDT, value: str):
        pass
