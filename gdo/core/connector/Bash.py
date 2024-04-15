from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server


class Bash(Connector):

    @classmethod
    def get_server(cls):
        return GDO_Server.get_by_connector('Bash')

