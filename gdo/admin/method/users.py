from gdo.base.GDO import GDO
from gdo.core.GDO_User import GDO_User
from gdo.table.MethodQueryTable import MethodQueryTable


class users(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_User.table()

