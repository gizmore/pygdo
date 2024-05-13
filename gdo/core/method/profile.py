from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User


class profile(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_User('for').not_null(),
        ]

    def get_user(self) -> GDO_User:
        return self.param_value('for')

    def gdo_execute(self):
        user = self.get_user()
        return self
