from gdo.base.Application import Application
from gdo.base.Logger import Logger


class Connector:
    AVAILABLE = {}  # Static all
    TEXT_CONNECTORS = []  # Static without web

    _server: object  # instance server
    _connected: bool
    _connecting: bool
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
        return cls.AVAILABLE[name.lower()]()

    ############
    # Instance #
    ############
    def __init__(self):
        super().__init__()
        self._connected = False
        self._connecting = False
        self._connect_failures = 0

    def gdo_has_channels(self) -> bool:
        return False

    def gdo_needs_authentication(self) -> bool:
        """
        Overwrite this if a connector needs explicit authentication. For example Web or IRC. Bash and Telegram is treated as authenticated already.
        """
        return True

    def gdo_connect(self) -> bool:
        return True

    def gdo_disconnect(self, quit_message: str):
        pass

    def gdo_disconnected(self):
        pass

    def get_name(self):
        return self.__class__.__name__

    def is_connected(self) -> bool:
        return self._connected

    def is_connecting(self) -> bool:
        return self._connecting

    def should_connect_now(self) -> bool:
        return Application.TIME >= self._next_connect_time

    def connect(self) -> bool:
        self._connecting = True
        if self.gdo_connect():
            self.connect_success()
        return self._connected

    def disconnect(self, quit_message: str = None) -> bool:
        """
        Actively disconnect
        """
        Logger.debug(f"disconnect({quit_message})")
        self.gdo_disconnect(quit_message or "PyGDO QUIT without further message")
        self._connected = False
        self._connecting = False
        self._connect_failures = 0
        self._next_connect_time = Application.TIME
        return True

    def connect_failed(self):
        self._connect_failures += 1
        self._next_connect_time = Application.TIME + (self._connect_failures * 10)
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

