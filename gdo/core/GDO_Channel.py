from gdo.base.GDO import GDO
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Char import GDT_Char
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.language.GDT_Language import GDT_Language


class GDO_Channel(GDO):

    _users: dict[str, GDO_User]

    def __init__(self):
        super().__init__()
        self._users = {}

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('chan_id'),
            GDT_Object('chan_server').table(GDO_Server.table()).not_null().cascade_delete(),
            GDT_Name('chan_name').not_null(),
            GDT_String('chan_displayname').maxlen(96).not_null(),
            GDT_Language('chan_language').not_null().initial('en'),
            GDT_Char('chan_trigger').maxlen(1).not_null().initial('$'),
            GDT_Created('chan_created'),
            GDT_Creator('chan_creator'),
        ]

    def get_trigger(self) -> str:
        return self.gdo_val('chan_trigger')

    def get_lang_iso(self) -> str:
        return self.gdo_val('chan_language')

    def get_server(self) -> GDO_Server:
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

    async def send(self, message: str):
        if Application.IS_HTTP:
            pass
            # GDO_Event.blank().insert()
        else:
            server = self.get_server()
            conn = server.get_connector()
            msg = Message(message, conn.get_render_mode())
            msg.env_user(GDO_User.system())
            msg.env_server(server).env_channel(self).result(message)
            await conn.send_to_channel(msg)

    def on_user_joined(self, user: GDO_User):
        user_name = user.get_name()
        if user_name not in self._users:
            self._users[user_name] = user
            Application.EVENTS.publish('user_joined_channel', user, self)

    def on_user_left(self, user: GDO_User):
        user_name = user.get_name()
        del self._users[user_name]
        Application.EVENTS.publish('user_left_channel', user, self)
