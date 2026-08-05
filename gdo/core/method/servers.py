from gdo.base.GDO import GDO
from gdo.base.Render import Mode
from gdo.core.GDO_Server import GDO_Server
from gdo.message.GDT_Bold import GDT_Bold
from gdo.message.GDT_Colored import GDT_Colored
from gdo.message.GDT_Glyph import GDT_Glyph
from gdo.table.MethodQueryTable import MethodQueryTable


class servers(MethodQueryTable):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "servers"

    def gdo_table(self) -> GDO:
        return GDO_Server.table()

    def render_cli(self) -> str:
        server = self._gdo
        return f"{server.render_name()}"

    def render_irc(self) -> str:
        server = self._gdo
        return f"{server.render_name()}"

    def render_gdo(self, gdo: GDO_Server, mode: Mode) -> str:
        """Render the stable ID and the connector's current connection state."""
        server_id = GDT_Bold().add_field(GDT_Glyph(gdo.get_id())).render(mode)
        color = 'green' if gdo.get_connector().is_connected() else 'red'
        name = GDT_Colored(color).add_field(GDT_Glyph(gdo.get_name())).render(mode)
        return f'{server_id}-{name}'
