from gdo.core.GDT_Enum import GDT_Enum


class GDT_UserType(GDT_Enum):
    SYSTEM = 'system'
    GHOST = 'ghost'
    GUEST = 'guest'
    MEMBER = 'member'
    CHAPPY = 'chappy'
    BOT = 'bot'
    LINK = 'link'
    DEVICE = 'device'

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'system': 'System',
            'ghost': 'Ghost',
            'guest': 'Guest',
            'member': 'Member',
            'chappy': 'GPT',
            'bot': 'Bot',
            'link': 'Link',
            'device': 'Device',
        }
