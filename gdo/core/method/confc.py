from gdo.base.GDT import GDT
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

    def get_config(self, method: Method, key: str) -> GDT:
        return method.get_config_channel(key)

    def get_config_val(self, method: Method, key) -> str:
        return method.get_config_channel_val(key)

    def set_config_val(self, method: Method, key: str, val: str):
        method.save_config_channel(key, val)

    def delete_config_val(self, method: Method, key: str):
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
        from gdo.core.GDO_MethodValChannelBlob import GDO_MethodValChannelBlob
        from gdo.core.GDT_Text import GDT_Text
        gdt = method.get_config_channel(key)
        table = GDO_MethodValChannelBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValChannel.table()
        if entry := table.get_by_id(GDO_Method.for_method(method).get_id(), method._env_channel.get_id(), gdt.get_name()):
            entry.delete()
