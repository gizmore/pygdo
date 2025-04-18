from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.ui.GDT_Error import GDT_Error


class client_error(Method):
    """
    The client made an error. probably a wrong param.
    """
    _exception: Exception

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def exception(self, exception: Exception):
        self._exception = exception
        return self

    def gdo_execute(self) -> GDT:
        Application.status("400 Client Error")
        return GDT_Error.from_exception(self._exception)
