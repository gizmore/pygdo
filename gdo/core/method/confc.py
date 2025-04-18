from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.MethodConf import MethodConf


class confc(MethodConf):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'confc'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def get_configs(self, method: Method) -> list:
        return method._config_channel()

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_channel_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_channel(key, val)
