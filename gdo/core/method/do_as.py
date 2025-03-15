from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User


class do_as(Method):

    def gdo_trigger(self) -> str:
        return 'as'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_User('user').not_null(),
            GDT_RestOfText('cmd').not_null(),
        ]

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    async def gdo_execute(self) -> GDT:
        user = self.param_value('user')
        await Message(' '.join(self.param_val('cmd')), self._env_mode).env_copy(self).env_user(user, True).execute()
        return self.empty()
