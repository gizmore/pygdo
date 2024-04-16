from gdo.base.GDO_Module import GDO_Module
from gdo.core.Connector import Connector
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.InstallUser import InstallUser
from gdo.core.connector.Bash import Bash


class module_core(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 1

    def gdo_init(self):
        Connector.register(Bash)

    def gdo_dependencies(self) -> list:
        return [
            'base',
            'date',
            'language',
            'net',
        ]

    def gdo_classes(self):
        return [
            GDO_Server,
            GDO_User,
            GDO_Permission,
            GDO_UserPermission,
            GDO_Session,
        ]

    def gdo_install(self):
        InstallUser.now()

