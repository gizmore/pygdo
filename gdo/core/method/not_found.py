from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.net.GDT_Url import GDT_Url
from gdo.ui.GDT_Error import GDT_Error


class not_found(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Url("_url").not_null(),
        ]

    def gdo_execute(self):
        url = self.param_val('_url')
        return GDT_Error().title('module_core').text('err_not_found', [Strings.html(f'"{url}"')])
