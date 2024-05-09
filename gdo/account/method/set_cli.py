from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting


class set_cli(Method):

    def gdo_trigger(self) -> str:
        return 'set'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UserSetting('name').not_null(),
            GDT_String('value').not_null(),
        ]

    def gdo_execute(self):
        user = self._env_user
        name = self.param_val('name')

