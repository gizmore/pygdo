from gdo.core.GDT_Object import GDT_Object


class GDT_User(GDT_Object):

    def __init__(self, name):
        super().__init__(name)
        from gdo.core.GDO_User import GDO_User
        self.table(GDO_User.table())

