from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect


class GDT_Permission(GDT_ObjectSelect):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_Permission.table())
