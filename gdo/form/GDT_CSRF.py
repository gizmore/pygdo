from gdo.core.GDT_Field import GDT_Field


class GDT_CSRF(GDT_Field):

    def __init__(self, name='csrf'):
        super().__init__(name)
