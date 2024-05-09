from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_Text import GDT_Text


class GDO_MethodValChannelBlob(GDO):

    def gdo_columns(self) -> list[GDT]:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_Channel import GDO_Channel
        return [
            GDT_Object('mv_method').table(GDO_Method.table()).primary(),
            GDT_Object('mv_channel').table(GDO_Channel.table()).primary(),
            GDT_Name('mv_key').primary(),
            GDT_Text('mv_val'),
        ]

    def get_val(self):
        return self.gdo_val('mv_val')
