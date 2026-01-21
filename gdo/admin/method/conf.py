from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Util import html
from gdo.core.Connector import Connector
from gdo.core.GDT_String import GDT_String


class conf(Method):
    """
    Get the list of config, the list of config for a module, state of a config var or set a config var
    """
    @classmethod
    def gdo_trigger(cls) -> str:
        return "conf"

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').enabled().positional(),
            GDT_String('config_name').positional(),
            GDT_String('config_value').positional(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_execute(self) -> GDT:
        module = self.get_module()
        if not module:
            return self.list_all()
        config_name = self.param_val('config_name')
        if not config_name:
            return self.list_module(module)
        gdts = module.config_column_completed(config_name)
        if not gdts:
            return self.err('err_module_config_gdt', (html(config_name),))
        if len(gdts) > 1:
            return self.err('err_module_config_gdt_ambiguous', (html(config_name), ", ".join([gdt.get_name() for gdt in gdts])))
        gdt = gdts[0]
        value = self.param_val('config_value')
        if not value:
            return self.show_value(module, gdt)
        value = None if value.lower() == "none" else value
        return self.set_value(module, gdt, value)

    def list_all(self):
        loader = ModuleLoader.instance()
        all_ = {}
        for module in loader._cache.values():
            name = Render.bold(module.get_name, self._env_mode)
            confs = module.gdo_module_config()
            confs = [gdt for gdt in confs if gdt.is_writable()]
            if confs:
                if name not in all_:
                    all_[name] = []
                for gdt in confs:
                    all_[name].append(gdt.get_name())

        sorted_modules = {k: sorted(v) for k, v in sorted(all_.items())}
        output = ""
        for module, attributes in sorted_modules.items():
            output += f"{module}: {', '.join(attributes)}. "
        return self.reply('msg_all_modules_conf', (output.strip(),))

    def list_module(self, module: GDO_Module):
        name = Render.bold(module.render_name(), self._env_mode)
        confs = module.gdo_module_config()
        out = []
        for conf in confs:
            out.append(conf.get_name() + "(" + Render.italic(conf.render_val(), self._env_mode) + ")")
        return self.reply('msg_module_conf', (name, ", ".join(out)))

    def show_value(self, module: GDO_Module, gdt: GDT):
        tt = ''
        if gdt.has_tooltip():
            tt = f" ({gdt.get_tooltip_text()})"
        val = Render.italic(gdt.render_val(), self._env_mode)
        return self.reply('msg_module_conf_options', (module.render_name(), gdt.get_name(), tt, val, gdt.render_suggestion()))

    def set_value(self, module: GDO_Module, gdt: GDT, value: str):
        val = gdt.to_val(gdt.to_value(value))
        old = Render.italic(gdt.render_val(), self._env_mode)
        module.save_config_val(gdt.get_name(), val)
        new = Render.italic(gdt.display_val(val), self._env_mode)
        if old == new:
            return self.reply('msg_module_conf_no_change', (gdt.get_name(), module.render_name(), old))
        return self.reply('msg_module_conf_changed', (module.render_name(), gdt.get_name(), old, new))
