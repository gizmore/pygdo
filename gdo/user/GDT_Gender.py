from gdo.core.GDT_Enum import GDT_Enum


class GDT_Gender(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'male': 'Male',
            'female': 'Female',
            'tm': 'Trans Male',
            'tf': 'Trans Female',
            'hermaphrodite': 'Hermaphrodite',
            'asexual': 'Asexual',
        }
