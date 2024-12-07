from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_String import GDT_String
from gdo.core.MethodConf import MethodConf


class confu(MethodConf):

    def gdo_trigger(self) -> str:
        return 'confu'

    def get_configs(self, method: Method) -> list:
        return method._config_user()
