from gdo.core.GDT_Enum import GDT_Enum


class GDT_UserType(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'system': 'System',
            'guest': 'Guest',
            'member': 'Member',
            'bot': 'Bot',
        }
