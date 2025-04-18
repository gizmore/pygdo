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

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_server_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_server(key, val)
