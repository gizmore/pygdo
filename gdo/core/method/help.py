import re

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Util import html
from gdo.core.Connector import Connector
from gdo.core.GDT_String import GDT_String


class help(Method):

    def gdo_trigger(self) -> str:
        return 'help'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_String('trigger').positional(),
        ]

    def get_trigger(self):
        return self.param_val('trigger')

    def gdo_execute(self) -> GDT:
        trigger = self.get_trigger()
        if trigger:
            return self.show_help_for(trigger)
        else:
            return self.show_all_commands()

    def show_help_for(self, trigger) -> GDT:
        loader = ModuleLoader.instance()
        if method := loader.get_method(trigger):
            mode = Application.get_mode()
            method.env_copy(self)
            usage = method.render_cli_usage()
            return GDT_String('help').text('msg_help_for', (Render.bold(trigger, mode), method.gdo_render_descr(), usage))
        else:
            return self.err('err_module', (html(trigger)))

    def show_all_commands(self):
        loader = ModuleLoader.instance()
        grouped = {}
        mode = self._env_mode
        for cmd, method in loader._methods.items():
            module_name = method.gdo_module().render_name()
            method.env_copy(self)
            if method.allows_connector() and not method.gdo_method_hidden():
                trigger = method.gdo_trigger()
                if module_name not in grouped:
                    grouped[module_name] = []
                if method.has_permission(self._env_user, False):
                    trigger_colored = Render.green(trigger, mode)
                else:
                    trigger_colored = Render.red(trigger, mode)
                grouped[module_name].append([trigger, trigger_colored])

        grouped_sorted = {module: sorted(triggers, key=lambda x: x[0]) for module, triggers in sorted(grouped.items())}

        group_part_one = {}
        for module, triggers in grouped_sorted.items():
            module_bold = Render.bold(module, mode)
            group_part_one[module_bold] = ", ".join(trigger_colored for _, trigger_colored in triggers)

        group_rendered = ", ".join(f"{module}: {triggers}" for module, triggers in group_part_one.items())

        return GDT_String('help').text('msg_help_all_commands', (group_rendered,))
