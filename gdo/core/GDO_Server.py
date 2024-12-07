import asyncio
from typing import TYPE_CHECKING

from gdo.base.Logger import Logger
from gdo.core.GDT_Bool import GDT_Bool

if TYPE_CHECKING:
    from gdo.core.Connector import Connector
    from gdo.core.GDO_Channel import GDO_Channel

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Trans import tusr
from gdo.core.Connector import Connector
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Char import GDT_Char
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_UserType import GDT_UserType
from gdo.date.GDT_Created import GDT_Created
from gdo.net.GDT_Url import GDT_Url


class GDO_Server(GDO):
    _connector: Connector
    _channels: list['GDO_Channel']
    _has_loop: bool

    __slots__ = (
        '_connector',
        '_channels',
    )

    def __init__(self):
        super().__init__()
        self._channels = []
        self._has_loop = False

    @classmethod
    def get_by_connector(cls, name: str):
        return cls.table().get_by_vals({"serv_connector": name})

    def gdo_columns(self) -> list[GDT]:
        from gdo.core.GDT_Creator import GDT_Creator
        return [
            GDT_AutoInc('serv_id'),
            GDT_Name('serv_name').unique(),
            GDT_Url('serv_url').in_and_external(),
            GDT_Char('serv_trigger').initial('$'),
            GDT_Name('serv_username'),
            GDT_Secret('serv_password'),
            GDT_Connector('serv_connector'),
            GDT_Bool('serv_enabled').not_null().initial('1'),
            GDT_Created('serv_created'),
            # GDT_Creator('serv_creator'),
        ]

    def get_name(self) -> str:
        return self.gdo_val('serv_name')

    def get_trigger(self) -> str:
        return self.gdo_val('serv_trigger')

    def get_username(self):
        return self.gdo_val('serv_username') or 'Dog'

    def get_url(self) -> dict:
        return self.gdo_value('serv_url')

    def get_connector(self) -> Connector:
        if not hasattr(self, '_connector'):
            self._connector = self.gdo_value('serv_connector')
            self._connector.server(self)
        return self._connector

    ########
    # User #
    ########

    def get_or_create_user(self, username: str, displayname: str = None, user_type: str = GDT_UserType.MEMBER):
        user = self.get_user_by_name(username)
        if not user:
            user = self.create_user(username, displayname or username, user_type)
        return user

    def create_user(self, username: str, displayname: str = None, user_type: str = GDT_UserType.MEMBER):
        user = GDO_User.blank({
            'user_type': user_type,
            'user_name': username,
            'user_displayname': displayname or username,
            'user_server': self.get_id(),
        }).insert()
        Application.EVENTS.publish('user_created', user)
        return user

    def get_user_by_name(self, username) -> GDO_User:
        return GDO_User.table().get_by_vals({
            'user_server': self.get_id(),
            'user_name': username,
        })

    def get_user_by_login(self, login: str) -> GDO_User | None:
        user = self.get_user_by_name(login)
        if not user:
            user = self.get_user_with_settings([('email', '=', login), ('email_confirmed', 'IS NOT', None)])
        return user

    def get_user_with_settings(self, vals: list[tuple]) -> GDO_User | None:
        return GDO_UserSetting.get_user_with_settings(self.get_id(), vals)

    ###########
    # Channel #
    ###########
    def get_or_create_channel(self, name: str, display_name: str = None):
        from gdo.core.GDO_Channel import GDO_Channel
        channel = self.get_channel_by_name(name)
        if not channel:
            print(f"NO CHAN for {name}!")
            channel = GDO_Channel.blank({
                'chan_name': name,
                'chan_displayname': display_name or name,
                'chan_server': self.get_id(),
            }).insert()
        return channel

    def get_channel_by_name(self, name: str):
        from gdo.core.GDO_Channel import GDO_Channel
        return GDO_Channel.table().get_by_vals({
            'chan_server': self.get_id(),
            'chan_name': name,
        })

    ########
    # Loop #
    ########
    async def loop(self):
        conn = self.get_connector()
        while Application.RUNNING:
            # Logger.debug(f"{self.get_name()} loop")
            if not conn.is_connected():
                if not conn.is_connecting():
                    if conn.should_connect_now():
                        conn.connect()
            await asyncio.sleep(2)

    ###########
    # Message #
    ###########
    def send_to_user(self, user: GDO_User, key: str, args: list = None, reply_to: str = None):
        text = tusr(user, key, args)
        message = Message(text, Application.get_mode())
        message.env_user(user).env_server(self).env_channel(None).env_reply_to(reply_to)
        self.get_connector().send_to_user(message.result(text))

    ##########
    # Render #
    ##########
    def render_name(self) -> str:
        return f"{self.get_id()}-{self.get_name()}"
