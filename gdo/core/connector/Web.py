from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server


class Web(Connector):

    def get_render_mode(self) -> Mode:
        return Mode.HTML

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('Web')

    def gdo_connect(self):
        self._connected = True
        return True
