from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
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

    def show_all_commands(self):
        loader = ModuleLoader.instance()
        grouped = {}
        for cmd, fqn in loader._methods.items():
            if not fqn in grouped:
                grouped[fqn] = cmd
        return GDT_NotImplemented()

