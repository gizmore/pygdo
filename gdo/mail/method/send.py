from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_User import GDT_User
from gdo.ui.GDT_Title import GDT_Title


class send(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_User("to"),
            GDT_Title("subject"),

        ]
