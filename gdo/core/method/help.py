import re

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.core.Connector import Connector
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String


class help(Method):

    def gdo_trigger(self) -> str:
        return 'help'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_String('trigger').positional(),
        ]

    def get_trigger(self):
        return self.param_val('trigger')

    def gdo_execute(self):
        trigger = self.get_trigger()
        if trigger:
            return self.show_help_for(trigger)
        else:
            return self.show_all_commands()

    def show_help_for(self, trigger):
        loader = ModuleLoader.instance()
        method = loader.get_method(trigger)
        mode = Application.get_mode()
        method.env_copy(self)
        parser = method.get_arg_parser(True)
        usage = parser.format_usage().rstrip()
        usage = usage.replace("\n", '')
        usage = re.sub(r'\s+', ' ', usage)
        return GDT_String('help').text('msg_help_for', [Render.bold(trigger, mode), method.gdo_render_descr(), usage])

    def show_all_commands(self):
        loader = ModuleLoader.instance()
        grouped = {}
        mode = Application.get_mode()
        user = self._env_user
        for cmd, method in loader._methods.items():
            module_name = method.module().render_name()
            trigger = method.env_user(user).gdo_trigger()
            if module_name not in grouped:
                grouped[module_name] = []
            if self.has_permission(self._env_user):
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

        return GDT_String('help').text('msg_help_all_commands', [group_rendered])
