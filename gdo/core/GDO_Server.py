from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Name import GDT_Name
from gdo.date.GDT_Created import GDT_Created


class GDO_Server(GDO):

    def __init__(self):
        super().__init__()

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('serv_id'),
            GDT_Name('serv_name'),
            GDT_Connector('serv_connector'),
            GDT_Created('serv_created'),
            GDT_Creator('serv_creator'),
        ]
