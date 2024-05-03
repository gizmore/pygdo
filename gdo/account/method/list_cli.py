from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting


class list_cli(Method):

    def gdo_trigger(self) -> str:
        return 'settings'

    def gdo_parameters(self) -> [GDT]:
        return [
        ]
