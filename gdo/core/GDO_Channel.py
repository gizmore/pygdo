from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Char import GDT_Char
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created


class GDO_Channel(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('chan_id'),
            GDT_Object('chan_server').table(GDO_Server.table()).not_null(),
            GDT_Name('chan_name').not_null(),
            GDT_String('chan_displayname').not_null(),
            GDT_Char('chan_trigger').maxlen(1).not_null().initial('$'),
            GDT_Created('chan_created'),
            GDT_Creator('chan_creator'),
        ]

    def get_trigger(self) -> str:
        return self.gdo_val('chan_trigger')

    def get_server(self):
        return self.gdo_value('chan_server')

    def get_name(self) -> str:
        return self.gdo_val('chan_name')

    def render_name(self):
        return self.gdo_val('chan_displayname')

    @classmethod
    def with_setting(cls, server: GDO_Server, key: str, val: str, default: str = '') -> list['GDO_Channel']:
        from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
        null = ' OR mv_val IS NULL' if default == val else ''
        query = (GDO_MethodValChannel.table().select('mv_channel_t.*').join_object('mv_channel')
                 .where(f"mv_key={cls.quote(key)}")
                 .where(f"mv_val={cls.quote(val)}{null}")
                 .where(f'chan_server={server.get_id()}'))
        return query.gdo(GDO_Channel.table()).exec().fetch_all()
