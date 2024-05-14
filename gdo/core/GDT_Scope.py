from gdo.core.GDT_Enum import GDT_Enum


class GDT_Scope(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self):
        return {'bot': 'Bot', 'server': 'Server', 'channel': 'Channel', 'user': 'User'}