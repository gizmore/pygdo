from gdo.core.GDT_String import GDT_String


class GDT_HTML(GDT_String):

    def __init__(self):
        super().__init__('HTML')

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration
