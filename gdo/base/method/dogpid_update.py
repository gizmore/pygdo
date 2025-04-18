from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.IPC import IPC
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting


class dogpid_update(Method):

    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> [GDT]:
        return [
        ]

    def gdo_execute(self) -> GDT:
        IPC.PID = 0
        return self.empty()
