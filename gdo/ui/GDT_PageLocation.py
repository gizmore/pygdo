from gdo.base.Application import Application
from gdo.core.GDT_Enum import GDT_Enum


class GDT_PageLocation(GDT_Enum):

    def gdo_choices(self) -> dict:
        return {
            '_title_bar': 'Head',
            '_top_bar': 'Top',
            '_left_bar': 'Left',
            '_right_bar': 'Right',
            '_bottom_bar': 'Foot',
        }

    def get_value(self):
        return getattr(Application.get_page(), self.get_val())
