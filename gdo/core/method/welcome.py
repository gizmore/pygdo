from gdo.base.Cache import gdo_cached
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.ui.GDT_Success import GDT_Success


class welcome(Method):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_execute(self) -> GDT:
        return GDT_Success().text('msg_gdo_working')
