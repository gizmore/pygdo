import re
import socket
import ssl

import httplib2

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

    TLS_SCHEMES = ('tls', 'https', 'ircs')

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

    def schemes(self, schemes: list[str]):
        self._url_schemes = schemes
        return self

    def all_schemes(self):
        self._url_schemes = []
        return self

    def reachable(self, exists: bool = True):
        self._url_reachable = exists
        return self

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

    def validate(self, value):
        if not super().validate(value):
            return False
        elif value is None:
            return True
        elif isinstance(value, str):
            return self.error('err_url_pattern')
        elif not self.validate_scheme(value):
            return False
        elif not self.validate_exists(value):
            return False
        else:
            return True

    def validate_scheme(self, url: dict):
        if len(self._url_schemes) == 0:
            return True
        if url['scheme'] not in self._url_schemes:
            self.error('err_url_scheme', [html(url['scheme'])])
            return False
        return True

    def validate_exists(self, url):
        if url['scheme'].startswith('http'):
            return self.validate_http_exists(url)
        elif url['tls']:
            return self.validate_tls_exists(url)
        else:
            return self.validate_plain_exists(url)

    def validate_http_exists(self, url):
        try:
            http = httplib2.Http()
            response, content = http.request(url['scheme'] + '://' + url['host'] + ':' + str(url['port']) + url['path'], method='HEAD')
            if response.status < 400:
                return True
            else:
                self.error('err_http_url_available', [html(url['host']), url['port'], response.status])
                return False
        except httplib2.HttpLib2Error:
            self.error('err_http_url_available', [html(url['host']), url['port'], "unknown"])
            return False

    def validate_plain_exists(self, url):
        try:
            with socket.create_connection((url['host'], url['port'])) as sock:
                return True
        except (socket.timeout, ConnectionError, OSError):
            self.error('err_url_available', [html(url['host']), url['port']])
            return False

    def validate_tls_exists(self, url) -> bool:
        try:
            with socket.create_connection((url['host'], url['port'])) as sock:
                with ssl.create_default_context().wrap_socket(sock, server_hostname=url['host']) as tls_sock:
                    return True  # TLS connection successful, URL with TLS exists
        except (socket.timeout, ConnectionError, OSError, ssl.SSLError):
            self.error('err_url_available', [html(url['host']), url['port']])
        return False
