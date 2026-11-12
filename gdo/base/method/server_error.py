import sys

from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Util import html
from gdo.ui.GDT_Error import GDT_Error


class server_error(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def gdo_execute(self) -> GDT:
        exception = sys.exception()
        if exception is None:
            return GDT_Error().text_raw('Internal server error.')
        return GDT_Error().text_raw(f'<pre>{html(Logger.traceback(exception, show_locals=False))}</pre>')
