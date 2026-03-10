import ipaddress

from gdo.base.Application import Application
from gdo.core.GDT_String import GDT_String


class GDT_IP(GDT_String):
    _use_current_ip: bool
    _format: int

    FORMAT_ASCII = 1
    FORMAT_BINARY = 2

    def __init__(self, name: str):
        super(GDT_IP, self).__init__(name)
        self.minlen(3)
        self.maxlen(39)
        self.ascii()
        self._pattern = '/^[0-9.:]*$/'
        self._use_current_ip = False
        self._format = self.FORMAT_ASCII

    def binary(self):
        self._min_len = 4
        self._max_len = 16
        self._format = self.FORMAT_BINARY
        return super().binary()

    def gdo_column_define(self) -> str:
        if self._format == self.FORMAT_BINARY:
            return (f"{self._name} BINARY({self._max_len}) "
                    f"{self.gdo_column_define_default()} "
                    f"{self.gdo_column_define_null()} ")
        return (f"{self._name} {self.gdo_varchar_define()}({self._max_len}) "
                f"CHARSET {self.gdo_column_define_charset()} {self.gdo_column_define_collate()} "
                f"{self.gdo_column_define_default()} "
                f"{self.gdo_column_define_null()} ")


    def use_current(self, use_current: bool = True):
        self._use_current_ip = use_current
        return self

    @staticmethod
    def ip_to_packed(value: str) -> bytes:
        """
        ASCII ip -> packed bytes.
        IPv4 => 4 bytes, IPv6 => 16 bytes.
        Accepts IPv6 zone ids (fe80::1%eth0) by stripping %...
        """
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value)

        s = str(value).strip()
        if '%' in s:  # zone id
            s = s.split('%', 1)[0]

        addr = ipaddress.ip_address(s)  # raises ValueError on invalid
        return addr.packed

    @staticmethod
    def packed_to_ip(val: bytes) -> str:
        """
        packed bytes -> canonical ASCII ip.
        4 bytes => IPv4, 16 bytes => IPv6.
        """
        if val is None:
            return None
        if isinstance(val, memoryview):
            val = val.tobytes()
        else:
            val = bytes(val)

        ln = len(val)
        if ln == 4:
            return str(ipaddress.IPv4Address(val))
        if ln == 16:
            return str(ipaddress.IPv6Address(val))
        raise ValueError(f"Invalid packed IP length: {ln} (expected 4 or 16)")

    def to_val(self, value):
        if self._format == self.FORMAT_BINARY:
            return self.ip_to_packed(value)
        return super().to_val(value)

    def to_value(self, val: str):
        if self._use_current_ip and val is None:
            return self.current()
        if self._format == self.FORMAT_BINARY:
            return self.packed_to_ip(val)
        return val

    def get_initial(self):
        if self._use_current_ip and not self._initial:
            return self.to_val(self.current())
        return self._initial

    @classmethod
    def current(cls) -> str:
        return Application.storage('ip', '::1')
