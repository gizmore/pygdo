from gdo.base.Application import Application
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserType import GDT_UserType


class InstallCore:

    @classmethod
    def now(cls):
        cls.install_bash()
        cls.install_system()
        cls.install_web()
        cls.install_perms()

    @classmethod
    def install_system(cls):
        if not GDO_User.system().get_id():
            GDO_User.blank({
                'user_type': GDT_UserType.SYSTEM,
                'user_name': 'System',
                'user_displayname': 'System',
                'user_server': GDO_Server.get_by_connector('Bash').get_id(),
            }).insert()

    @classmethod
    def install_bash(cls):
        if not GDO_Server.get_by_connector('Bash'):
            Application.SERVER = GDO_Server.blank({
                'serv_name': 'Bash',
                'serv_connector': 'Bash',
            }).insert()


    @classmethod
    def install_web(cls):
        if not GDO_Server.get_by_connector('Web'):
            GDO_Server.blank({
                'serv_name': 'Web',
                'serv_connector': 'Web',
            }).insert()

    @classmethod
    def install_perms(cls):
        cls.install_perm(GDO_Permission.ADMIN)
        cls.install_perm(GDO_Permission.STAFF)
        cls.install_perm(GDO_Permission.CRONJOB)

    @classmethod
    def install_perm(cls, name):
        if not GDO_Permission.table().get_by_name(name):
            GDO_Permission.blank({
                'perm_name': name
            }).insert()
