from gdo.core.GDT_Enum import GDT_Enum


class GDT_Gender(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)
        self._simple = False

    def simple(self, simple: bool = True):
        self._simple = simple
        return self

    def gdo_choices(self) -> dict:
        if self._simple:
            return {
                'male': 'Male',
                'female': 'Female',
            }
        return {
            'male': 'Male',
            'female': 'Female',
            'tm': 'Trans Male',
            'tf': 'Trans Female',
            'hermaphrodite': 'Hermaphrodite',
            'asexual': 'Asexual',
        }
