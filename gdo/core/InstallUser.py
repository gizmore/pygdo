from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserType import GDT_UserType


class InstallUser:

    @classmethod
    def now(cls):
        cls.install_bash()
        cls.install_system()
        cls.install_web()

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
            GDO_Server.blank({
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
