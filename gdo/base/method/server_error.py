import traceback

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.ui.GDT_Error import GDT_Error


class server_error(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def gdo_execute(self) -> GDT:
        from gdo.base import module_base
        if module_base.instance().cfg_500_mails():
            pass
        return GDT_Error().text_raw(traceback.format_exc())
