from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect


class GDT_Channel(GDT_ObjectSelect):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_Channel.table())
