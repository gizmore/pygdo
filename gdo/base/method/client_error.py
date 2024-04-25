import traceback

from gdo.base.Method import Method
from gdo.ui.GDT_Error import GDT_Error


class client_error(Method):
    """
    The client made an error. probably a wrong param.
    """
    _exception: Exception

    def exception(self, exception: Exception):
        self._exception = exception
        return self

    def gdo_execute(self):
        return GDT_Error.from_exception(self._exception)
