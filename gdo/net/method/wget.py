import httplib2

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.core.GDT_Select import GDT_Select
from gdo.net.GDT_Url import GDT_Url
from gdo.ui.GDT_HTML import GDT_HTML


class wget(Method):

    def gdo_trigger(self) -> str:
        return 'wget'

    def gdo_parameters(self):
        return [
            GDT_Select('method').choices({'HEAD': 'HEAD', 'GET': 'GET', 'POST': 'POST'}).not_null().initial('GET'),
            GDT_Url('url').in_and_external().not_null(),
        ]

    def gdo_execute(self) -> GDT:
        url = self.param_value('url')
        method = self.param_val('method')
        http = httplib2.Http()
        response, content = http.request(url['scheme'] + '://' + url['host'] + ':' + str(url['port']) + url['path'], method=method)
        encoding = self.parse_encoding(response)
        return GDT_HTML().val(content.decode(encoding))

    def parse_encoding(self, response: httplib2.Response):
        try:
            ct = response.get('content-type')
            return Strings.regex_first("charset=(.*)", ct)
        except Exception:
            return 'utf-8'

