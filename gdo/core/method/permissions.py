from gdo.base.GDO import GDO
from gdo.core.GDO_Permission import GDO_Permission
from gdo.table.MethodQueryTable import MethodQueryTable


class permissions(MethodQueryTable):

    def gdo_trigger(self) -> str:
        return 'perms'

    def gdo_table(self) -> GDO:
        return GDO_Permission.table()
