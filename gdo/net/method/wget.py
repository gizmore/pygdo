from gdo.base.Method import Method
from gdo.core.GDT_Select import GDT_Select
from gdo.net.GDT_Url import GDT_Url


class wget(Method):

    def gdo_trigger(self) -> str:
        return 'wget'

    def gdo_parameters(self):
        return [
            GDT_Select('method').choices({'HEAD': 'HEAD', 'GET': 'GET', 'POST': 'POST'}).not_null().initial('GET'),
            GDT_Url('url').not_null(),
        ]

    def execute(self):
        url = self.param_value('url')

