from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Password import GDT_Password
from gdo.net.GDT_Url import GDT_Url


class add_server(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "add_server"

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Name('username'),
            GDT_Password('password'),
            GDT_Name('name').not_null(),
            GDT_Connector('connector').not_null(),
            GDT_Url('url').all_schemes().in_and_external().reachable().positional(),
        ]

    def get_server_name(self):
        return self.param_val('name')

    def get_server_username(self):
        return self.param_val('username')

    def get_server_password(self):
        return self.param_val('password')

    def get_connector(self):
        return self.param_value('connector')

    def get_url(self):
        return self.param_val('url')

    def gdo_execute(self) -> GDT:
        conn = self.get_connector()
        server = GDO_Server.blank({
            'serv_name': self.get_server_name(),
            'serv_url': self.get_url(),
            'serv_username': self.get_server_username(),
            'serv_password': self.get_server_password(),
            'serv_connector': conn.get_name(),
        }).insert()
        return self.msg('msg_added_dog_server', (conn.get_name(), self.get_server_name(), server.get_id()))
