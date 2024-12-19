import re
import socket
import ssl

import httpx

from gdo.base.Application import Application
from gdo.base.Util import html, Strings
from gdo.core.GDT_String import GDT_String


class GDT_Url(GDT_String):
    """
    Parses url into a dictionary.
    """

    DEFAULT_PORTS = {
        '': 0,
        'ssh': 22,
        'http': 80,
        'https': 443,
        'irc': 6667,
        'ircs': 6697,
    }

    TLS_SCHEMES = ('https', 'ircs', 'tcps', 'tls', 'ssh')

    URL_PATTERN = re.compile(
        r'(?P<scheme>\w+)://(?P<host>[\w.-]+)(?::(?P<port>\d+))?'
        r'(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?(?:#.*)?'
    )

    @classmethod
    def default_port(cls, scheme: str) -> int:
        return cls.DEFAULT_PORTS[scheme]

    _url_schemes: list[str]
    _url_reachable: bool
    _url_external: bool
    _url_internal: bool

    def __init__(self, name):
        super().__init__(name)
        self._url_schemes = ['http', 'https']
        self._url_reachable = False
        self._url_internal = False
        self._url_external = False

    def schemes(self, schemes: list[str]):
        self._url_schemes = schemes
        return self

    def all_schemes(self):
        self._url_schemes = []
        return self

    def reachable(self, exists: bool = True):
        self._url_reachable = exists
        return self

    def in_and_external(self):
        self._url_internal = True
        self._url_external = True
        return self

    def internal(self, internal: bool = True):
        self._url_internal = internal
        return self

    def external(self, external: bool = True):
        self._url_external = external
        return self

    #######
    # GDT #
    #######

    def val(self, val: str):
        if val.startswith('/'):
            val = Application.PROTOCOL + '://' + Application.config('core.domain') + val
        return super().val(val)

    def to_value(self, val: str):
        """
        TODO: Make GDT.to_value() IPv6 ready
        """
        if val is None:
            return None
        match = GDT_Url.URL_PATTERN.match(val)
        if not match:
            return val
        scheme = match.group('scheme')
        host = match.group('host')
        port = match.group('port')
        path = match.group('path')
        query = match.group('query')
        if port is None:
            port = GDT_Url.default_port(scheme)
        return {
            'raw': val,
            'scheme': scheme,
            'host': host,
            'port': int(port),
            'path': path or '/',
            'query': query,
            'tls': scheme in GDT_Url.TLS_SCHEMES,
            'ipv': 4,
        }

    ############
    # Validate #
    ############

    async def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
            return False
        elif value is None:
            return True
        elif isinstance(value, str):
            return self.error('err_url_pattern')
        elif not self.validate_scheme(value):
            return False
        elif not await self.validate_exists(value):
            return False
        elif not self.validate_internal_external(value):
            return False
        else:
            return True

    def validate_scheme(self, url: dict) -> bool:
        if len(self._url_schemes) == 0:
            return True
        if url['scheme'] not in self._url_schemes:
            return self.error('err_url_scheme', [html(url['scheme'])])
        return True

    async def validate_exists(self, url) -> bool:
        if url['scheme'].startswith('http'):
            return await self.validate_http_exists(url)
        elif url['tls']:
            return await self.validate_tls_exists(url)
        else:
            return await self.validate_plain_exists(url)

    async def validate_http_exists(self, url) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url['scheme'] + '://' + url['host'] + ':' + str(url['port']) + url['path'])
            if response.status_code < 400:
                return True
            else:
                return self.error('err_http_url_available', [html(url['raw']), f"HTTP ERROR {response.status_code}"])
        except Exception as ex:
            return self.error('err_http_url_available', [html(url['raw']), f"ERROR: {str(ex)}"])

    async def validate_plain_exists(self, url) -> bool:
        try:
            with socket.create_connection((url['host'], url['port'])) as sock:
                return True
        except (socket.timeout, ConnectionError, OSError):
            return self.error('err_url_available', [html(url['raw'])])

    async def validate_tls_exists(self, url) -> bool:
        try:
            with socket.create_connection((url['host'], url['port'])) as sock:
                with ssl.create_default_context().wrap_socket(sock, server_hostname=url['host']) as tls_sock:
                    return True  # TLS connection successful, URL with TLS exists
        except (socket.timeout, ConnectionError, OSError, ssl.SSLError):
            self.error('err_url_available', [html(url['raw'])])
        return False

    def validate_internal_external(self, url: dict) -> bool:
        if not self._url_internal:
            if url['host'] == Application.config('core.domain'):
                return self.error('err_url_no_internals')
        if not self._url_external:
            if url['host'] != Application.config('core.domain'):
                return self.error('err_url_no_externals')
        return True
