import re

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOParamError
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Util import html
from gdo.core.Connector import Connector
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String
from gdo.language.GDT_Trans import GDT_Trans
from gdo.message.GDT_Bold import GDT_Bold
from gdo.message.GDT_Colored import GDT_Colored
from gdo.message.GDT_Glyph import GDT_Glyph
from gdo.message.GDT_Span import GDT_Span


class help(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'help'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Bool('short').not_null().initial('0'),
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
        meths = loader._meths if self.param_value('short') else loader._methods
        for klass in meths.values():
            method = klass()
            module_name = method.gdo_module().render_name()
            method.env_copy(self)
            if method.allows_connector() and not method.gdo_method_hidden():
                trigger = method.gdo_trigger()
                if module_name not in grouped:
                    grouped[module_name] = []
                # Some commands decide permissions from a required argument
                # (for example Logs/UserMethod).  `$help` has no argument to
                # supply here, so list those commands as unavailable instead
                # of aborting the complete command list.
                try:
                    allowed = method.has_permission(self._env_user, False)
                except GDOParamError:
                    allowed = False
                if allowed:
                    trigger_colored = 'green'
                else:
                    trigger_colored = 'red'
                grouped[module_name].append([trigger, trigger_colored])

        grouped_sorted = {module: sorted(triggers, key=lambda x: x[0]) for module, triggers in sorted(grouped.items())}

        output = GDT_Span().add_field(GDT_Trans().text('msg_help_commands_prefix'))
        for group_index, (module, triggers) in enumerate(grouped_sorted.items()):
            if group_index:
                output.add_field(GDT_Glyph(', '))
            output.add_field(GDT_Bold().add_field(GDT_Glyph(module)))
            output.add_field(GDT_Glyph(': '))
            for trigger_index, (trigger, color) in enumerate(triggers):
                if trigger_index:
                    output.add_field(GDT_Glyph(', '))
                output.add_field(GDT_Colored(color).add_field(GDT_Glyph(trigger)))
        return output.add_field(GDT_Trans().text('msg_help_commands_suffix'))
