from line_profiler_pycharm import profile

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Util import jsn
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_NotImplemented import GDT_NotImplemented
from gdo.core.GDT_String import GDT_String


class help(Method):

    def cli_trigger(self) -> str:
        return 'help'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_String('trigger'),
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
        return GDT_String('help').text('msg_help_form', [Render.bold(trigger, mode), method.gdo_render_usage()])

    @profile
    def show_all_commands(self):
        loader = ModuleLoader.instance()
        grouped = {}
        mode = Application.get_mode()
        user = GDO_User.current()
        for cmd, method in loader._methods.items():
            module_name = method.module().render_name()
            trigger = method.user(user).cli_trigger()
            if module_name not in grouped:
                grouped[module_name] = []
            if method.prepare():
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
