from gdo.core.GDT import GDT
from gdo.core.WithLabel import WithLabel


class GDT_Label(WithLabel, GDT):

    def __init__(self, name: str):
        super().__init__(name)

