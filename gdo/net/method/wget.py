from gdo.core.Method import Method
from gdo.net.GDT_Url import GDT_Url


class wget(Method):

    def gdo_parameters(self):
        return [
            GDT_Url('url').not_null(),
        ]

    def execute(self):

        url = self.gdo_parameter_value('url')


