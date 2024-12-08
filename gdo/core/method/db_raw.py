from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_RestOfText import GDT_RestOfText


class db_raw(Method):

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.ADMIN

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_RestOfText('sql').not_null(),
        ]

    def gdo_execute(self):
        return self.empty('not yet')
