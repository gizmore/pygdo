from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.MethodConf import MethodConf


class confs(MethodConf):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'confs'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.ADMIN

    def get_configs(self, method: Method) -> list:
        return method._config_server()

    def get_config(self, method: Method, key: str) -> GDT:
        return method.get_config_server(key)

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_server_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_server(key, val)

    def delete_config_val(self, method: Method, key: str):
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValServer import GDO_MethodValServer
        from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
        from gdo.core.GDT_Text import GDT_Text
        gdt = method.get_config_server(key)
        table = GDO_MethodValServerBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValServer.table()
        if entry := table.get_by_id(GDO_Method.for_method(method).get_id(), method._env_server.get_id(), gdt.get_name()):
            entry.delete()
