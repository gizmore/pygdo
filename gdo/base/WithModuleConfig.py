from gdo.base.Exceptions import GDOValidationException
from gdo.base.GDT import GDT


class WithModuleConfig:
    _module_config: dict[str, GDT]

    ############
    # Abstract #
    ############

    def gdo_module_config(self) -> list[GDT]:
        return []

    def gdo_user_config(self) -> list[GDT]:
        return []

    def gdo_user_settings(self) -> list[GDT]:
        return []

    ##########
    # Module #
    ##########

    def module_config(self) -> dict[str, GDT]:
        if not hasattr(self, '_module_config'):
            self._module_config = {}
            for gdt in self.gdo_module_config():
                self._module_config[gdt.get_name()] = gdt
        return self._module_config

    def config_column(self, key: str):
        return self.module_config().get(key)

    def get_config_val(self, key: str) -> str:
        return self.config_column(key).get_val()

    def get_config_value(self, key: str):
        return self.config_column(key).get_value()

    def save_config_val(self, key: str, val: str):
        from gdo.base.GDO_ModuleVal import GDO_ModuleVal
        gdt = self.config_column(key)
        if gdt.validate(val, gdt.to_value(val)):
            if val != self.get_config_val(key):
                GDO_ModuleVal.blank({
                    'mv_module': self.get_id(),
                    'mv_key': key,
                    'mv_val': val,
                }).replace()
                gdt.val(val)
        else:
            raise GDOValidationException(self.get_name(), key, val)
        return self

    def increase_config_val(self, key: str, by: int | float):
        old = self.get_config_value(key)
        return self.save_config_val(key, str(old + by))

    ########
    # User #
    ########

    def all_user_settings(self):
        from gdo.core.GDO_User import GDO_User
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        from gdo.core.GDT_Field import GDT_Field
        for gdt in self.gdo_user_settings():
            if isinstance(gdt, GDT_Field):
                yield GDO_UserSetting.setting_column(gdt.get_name(), GDO_User.current())
            else:
                yield gdt
        for gdt in self.gdo_user_config():
            if isinstance(gdt, GDT_Field):
                gdt = GDO_UserSetting.setting_column(gdt.get_name(), GDO_User.current())
                gdt.writable(False)
                yield gdt
            else:
                yield gdt
