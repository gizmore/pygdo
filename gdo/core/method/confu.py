from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.MethodConf import MethodConf


class confu(MethodConf):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'confu'

    def get_configs(self, method: Method) -> list:
        return method._config_user()

    def get_config(self, method: Method, key: str) -> GDT:
        return method.get_config_user(key)

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_user_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_user(key, val)

    def delete_config_val(self, method: Method, key: str):
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValUser import GDO_MethodValUser
        from gdo.core.GDO_MethodValUserBlob import GDO_MethodValUserBlob
        from gdo.core.GDT_Text import GDT_Text
        gdt = method.get_config_user(key)
        table = GDO_MethodValUserBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValUser.table()
        if entry := table.get_by_id(GDO_Method.for_method(method).get_id(), method._env_user.get_id(), gdt.get_name()):
            entry.delete()
