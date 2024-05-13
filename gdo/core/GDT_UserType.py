from gdo.core.GDT_Enum import GDT_Enum


class GDT_UserType(GDT_Enum):
    SYSTEM = 'system'
    GHOST = 'ghost'
    GUEST = 'guest'
    MEMBER = 'member'
    BOT = 'bot'
    LINK = 'link'

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'system': 'System',
            'guest': 'Guest',
            'member': 'Member',
            'bot': 'Bot',
        }
