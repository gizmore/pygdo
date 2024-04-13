from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_Object import GDT_Object


class GDT_Permission(GDT_Object):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_Permission.table())

