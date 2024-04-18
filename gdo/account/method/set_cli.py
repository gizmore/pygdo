from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting


class set_cli(Method):

    def cli_trigger(self) -> str:
        return 'set'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UserSetting('name').not_null(),
            GDT_String('value').not_null(),
        ]

    def gdo_execute(self):
        user = GDO_User.current()
        name = self.param_val('name')

