from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.method.launch import launch
from gdo.date.Time import Time


class stats(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'stats'

    def gdo_execute(self) -> GDT:
        app = Application

        num_servers = len(launch.SERVERS) or GDO_Server.table().count_where()
        con_servers = 0
        con_channel = 0
        con_users = 0
        for server in launch.SERVERS:
            if server.get_connector().is_connected():
                con_servers += 1
                con_channel += len(server._channels)
                con_users += len(server._users)

        return self.reply('msg_stats', (
            con_servers, num_servers, con_channel, con_users,
            Time.human_duration(app.runtime()),
            (app.DB_READS + app.DB_WRITES) / app.runtime()))
