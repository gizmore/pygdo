from gdo.base.Method import Method
from gdo.net.GDT_Url import GDT_Url


class wget(Method):

    def cli_trigger(self) -> str:
        return 'wget'

    def gdo_parameters(self):
        return [
            GDT_Url('url').not_null(),
        ]

    def execute(self):
        url = self.param_value('url')

