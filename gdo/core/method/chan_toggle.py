from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Bool import GDT_Bool


class chan_toggle(Method):
    """Toggle the Bash CLI between its pseudo channel and private mode."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'chan.toggle'

    def gdo_connectors(self) -> str:
        return 'bash'

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Bool('enabled').not_null().positional()]

    def gdo_execute(self) -> GDT:
        enabled = self.param_value('enabled')
        Application.STORAGE.cli_channel_mode = enabled
        return self.reply('msg_cli_channel_mode', (
            self.parameter('enabled').display_var(self.param_val('enabled')),
        ))
