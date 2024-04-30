from gdo.base.Application import Application


class Connector:
    AVAILABLE = {}  # Static all

    _server: object  # instance server
    _connected: bool
    _connecting: bool
    _connect_failures: int
    _next_connect_time: float

    @classmethod
    def register(cls, klass):
        cls.AVAILABLE[klass.__name__.lower()] = klass

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

