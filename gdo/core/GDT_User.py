from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDO_User import GDO_User


class GDT_User(GDT_Object):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_User.table())

