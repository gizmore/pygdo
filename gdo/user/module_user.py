from gdo.base.GDO_Module import GDO_Module
from gdo.user.GDO_User import GDO_User
from gdo.user.InstallUser import InstallUser


class module_user(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 3

    def gdo_classes(self):
        return [
            GDO_User,
        ]

    def gdo_install(self):
        InstallUser.now(self)
