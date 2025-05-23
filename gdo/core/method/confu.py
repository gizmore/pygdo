from gdo.base.Method import Method
from gdo.core.MethodConf import MethodConf


class confu(MethodConf):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'confu'

    def get_configs(self, method: Method) -> list:
        return method._config_user()

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_user_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_user(key, val)
