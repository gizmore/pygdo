import httplib2

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Select import GDT_Select
from gdo.net.GDT_Url import GDT_Url
from gdo.message.GDT_HTML import GDT_HTML


class wget(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'wget'

    def gdo_parameters(self):
        return [
            GDT_Bool('full').not_null().initial('0'),
            GDT_Select('method').choices({'HEAD': 'HEAD', 'GET': 'GET', 'POST': 'POST'}).not_null().initial('GET'),
            GDT_Url('url').in_and_external().not_null(),
        ]

    def gdo_execute(self) -> GDT:
        url = self.param_value('url')
        method = self.param_val('method')
        http = httplib2.Http()
        response, content = http.request(url['scheme'] + '://' + url['host'] + ':' + str(url['port']) + url['path'], method=method)
        encoding = self.parse_encoding(response)
        content = content.decode(encoding)
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
