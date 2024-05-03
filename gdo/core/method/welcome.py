from gdo.base.Method import Method
from gdo.ui.GDT_Success import GDT_Success


class welcome(Method):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_execute(self):
        return GDT_Success().text('msg_gdo_working')
