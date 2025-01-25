from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT


class module_form(GDO_Module):

    def __init__(self):
        super().__init__()
        self.priority = 7

    def gdo_user_config(self) -> list[GDT]:
        return [
        ]
