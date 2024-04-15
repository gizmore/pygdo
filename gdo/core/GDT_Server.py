from gdo.core.GDT_Object import GDT_Object


class GDT_Server(GDT_Object):
    def __init__(self, name):
        from gdo.core.GDO_Server import GDO_Server
        super().__init__(name)
        self.table(GDO_Server.table())
