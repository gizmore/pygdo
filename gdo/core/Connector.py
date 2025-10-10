from typing import TYPE_CHECKING

from gdo.base.Render import Mode
from gdo.core.GDO_User import GDO_User
from gdo.date.Time import Time

if TYPE_CHECKING:
    from gdo.core.GDO_Server import GDO_Server

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Message import Message


class Connector:
    AVAILABLE = {}  # Static all
    TEXT_CONNECTORS = []  # Static without web

    _server: 'GDO_Server|None'  # instance server
    _connected: bool
    _connecting: bool
    _tried_connecting: bool
    _connect_failures: int
    _next_connect_time: float

    @classmethod
    def text_connectors(cls) -> str:
        return ",".join(cls.TEXT_CONNECTORS)

    @classmethod
    def register(cls, klass, is_text: bool = True):
        name = klass.__name__.lower()
        if name not in cls.AVAILABLE:
            cls.AVAILABLE[name] = klass
            if is_text:
                cls.TEXT_CONNECTORS.append(name)

    @classmethod
    def get_by_name(cls, name: str):
        return cls.AVAILABLE[name.lower()]

    ############
    # Instance #
    ############
    def __init__(self):
        super().__init__()
        self._server = None
        self._connected = False
        self._connecting = False
        self._tried_connecting = False
        self._connect_failures = 0

    def __repr__(self):
        return f"{self.__class__.__name__}#{self._server}"

    def __eq__(self, other):
        return type(self) == type(other) and (self._server == other._server or (self._server is None and other._server is None))

    def get_render_mode(self) -> Mode:
        return Mode.TXT

    def gdo_has_channels(self) -> bool:
        return False

    def gdo_needs_authentication(self) -> bool:
        """
        Overwrite this if a connector needs explicit authentication. For example Web or IRC. Bash and Telegram is treated as authenticated already.
        """
        return True

    def gdo_connect(self) -> bool:
        self._connected = True
        return True

    def gdo_disconnect(self, quit_message: str):
        pass

    def gdo_disconnected(self):
        pass

    async def gdo_send_to_channel(self, msg: Message):
        Logger.debug(f"{self.get_name()} has stub send_to_channel()")

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        Logger.debug(f"{self.get_name()} has stub send_to_user()")

    def gdo_get_dog_user(self) -> GDO_User:
        return GDO_User.system()

    def get_name(self):
        return self.__class__.__name__.lower()

    def is_connected(self) -> bool:
        return self._connected

    def is_connecting(self) -> bool:
        return self._connecting

    def should_connect_now(self) -> bool:
        return Application.TIME >= self._next_connect_time

    def connect(self) -> bool:
        Logger.debug("Connector.connect()")
        self._connecting = True
        self._tried_connecting = True
        self.gdo_connect()
        if self._connected:
            self.connect_success()
        else:
            self.connect_failed()
        return self._connected

    def disconnect(self, quit_message: str = None) -> bool:
        """
        Actively disconnect
        """
        Logger.debug(f"disconnect({quit_message})")
        self.gdo_disconnect(quit_message or "PyGDO QUIT without further message")
        self.disconnected()
        return True

    def disconnected(self):
        self._connected = False
        self._connecting = False
        self._connect_failures = 0
        self._next_connect_time = Application.TIME
        self.gdo_disconnected()

    def connect_failed(self):
        self._connect_failures += 1
        self._next_connect_time = Application.TIME + (min(self._connect_failures * 10, Time.ONE_MINUTE*2))
        self._connecting = False

    def connect_success(self):
        self._connected = True
        self._connecting = False
        self._connect_failures = 0

    def server(self, server):
        if not hasattr(self, '_server'):
            self._server = server
            self._next_connect_time = Application.TIME
        return self

    async def send_to_channel(self, msg: Message, with_events: bool=True):
        await self.gdo_send_to_channel(msg)
        if with_events:
            Application.EVENTS.publish('msg_sent', msg)

    async def send_to_user(self, msg: Message, with_events: bool=True, notice: bool=False):
        await self.gdo_send_to_user(msg, notice)
        if with_events:
            Application.EVENTS.publish('msg_sent', msg)

    def is_user_online(self, user: GDO_User) -> bool:
        return user.get_name() in self._server._users
