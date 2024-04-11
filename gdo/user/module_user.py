from gdo.core.GDO_Module import GDO_Module
from gdo.user.GDO_User import GDO_User


class module_user(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 3

    def gdo_classes(self):
        return [
            GDO_User,
        ]

    def gdo_install(self):
        GDO_User.blank([])