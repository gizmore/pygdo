from gdo.base.GDO import GDO
from gdo.core.GDO_Server import GDO_Server
from gdo.table.MethodQueryTable import MethodQueryTable


class servers(MethodQueryTable):

    def gdo_trigger(self) -> str:
        return "servers"

    def gdo_table(self) -> GDO:
        return GDO_Server.table()

    def render_cli(self) -> str:
        server = self._gdo
        return f"{server.render_name()}"
    def render_irc(self) -> str:
        server = self._gdo
        return f"{server.render_name()}"
