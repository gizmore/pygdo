import os
import stat
from urllib.parse import unquote, urlsplit

import httplib2

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Select import GDT_Select
from gdo.core.GDT_String import GDT_String
from gdo.net.GDT_Url import GDT_Url
from gdo.message.GDT_HTML import GDT_HTML


class GDT_WgetUrl(GDT_Url):
    """HTTP URLs plus local file URLs; file access is authorized by wget."""

    @staticmethod
    def file_value(val):
        parts = urlsplit(val)
        path = unquote(parts.path)
        if (parts.scheme != 'file' or parts.netloc or parts.query or parts.fragment
                or not os.path.isabs(path) or '\x00' in path):
            return None
        return {'scheme': 'file', 'path': path}

    def validate(self, val):
        if val and val.lower().startswith('file:'):
            if not GDT_String.validate(self, val):
                return False
            return bool(self.file_value(val)) or self.error('err_url_pattern')
        return super().validate(val)

    def to_value(self, val):
        if val and val.lower().startswith('file:'):
            return self.file_value(val)
        return super().to_value(val)


class wget(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'wget'

    def gdo_parameters(self):
        return [
            GDT_Bool('full').not_null().initial('0'),
            GDT_Select('method').choices({'HEAD': 'HEAD', 'GET': 'GET', 'POST': 'POST'}).not_null().initial('GET'),
            GDT_WgetUrl('url').in_and_external().not_null().tooltip('tt_wget_url'),
        ]

    def gdo_execute(self) -> GDT:
        url = self.param_value('url')
        method = self.param_val('method')
        if url['scheme'] == 'file':
            if not self._env_user or not self._env_user.is_authenticated() or not self._env_user.has_permission('owner'):
                return self.err('err_wget_file_owner')
            if method != 'GET':
                return self.err('err_wget_file_get')
            try:
                fd = os.open(url['path'], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
                with os.fdopen(fd, 'rb') as file:
                    if not stat.S_ISREG(os.fstat(file.fileno()).st_mode):
                        raise ValueError('Not a regular file')
                    content = file.read(16385)
                if len(content) > 16384:
                    return self.err('err_wget_file_size')
                return GDT_HTML().text(content.decode('utf-8'))
            except (OSError, ValueError, UnicodeDecodeError):
                return self.err('err_wget_file_read')
        http = httplib2.Http()
        response, content = http.request(url['scheme'] + '://' + url['host'] + ':' + str(url['port']) + url['path'], method=method)
        encoding = self.parse_encoding(response)
        content = content.decode(encoding or 'utf-8')
        if not self.param_value('full'):
            content = self.html_to_text(content)
        return GDT_HTML().html(content)

    def parse_encoding(self, response: httplib2.Response):
        try:
            ct = response.get('content-type')
            return Strings.regex_first("charset=(.*)", ct)
        except:
            return 'utf-8'

    def html_to_text(self, html: str) -> str:
        return Strings.html_to_text(html)
